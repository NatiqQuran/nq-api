from rest_framework import serializers
from django.db import models
from datetime import datetime
from django.conf import settings

from quran.models import Mushaf, Surah, Ayah, Word, Translation, AyahTranslation, AyahBreaker, WordBreaker, Recitation, File, RecitationTimestamp, Status
from account.models import CustomUser

class MushafSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mushaf
        fields = ['uuid', 'short_name', 'name', 'source', 'status']
        read_only_fields = ['creator']

    def create(self, validated_data):
        return Mushaf.objects.create(**validated_data)

class SurahNameSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50)
    name_pronunciation = serializers.CharField(required=False, allow_null=True)
    name_translation = serializers.CharField(required=False, allow_null=True)
    name_transliteration = serializers.CharField(required=False, allow_null=True)

class SurahSerializer(serializers.ModelSerializer):
    names = serializers.SerializerMethodField(read_only=True)
    mushaf = MushafSerializer(read_only=True)
    mushaf_uuid = serializers.UUIDField(write_only=True, required=True)
    name = serializers.CharField(write_only=True, required=True)
    number_of_ayahs = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Surah
        fields = ['uuid', 'mushaf', 'mushaf_uuid', 'name', 'names', 'number', 'period', 'search_terms', 'number_of_ayahs']
        read_only_fields = ['creator']

    def get_number_of_ayahs(self, instance):
        return instance.ayahs.count()

    def get_names(self, instance):
        return [{
            'name': instance.name,
            'pronunciation': instance.name_pronunciation,
            'translation': instance.name_translation,
            'transliteration': instance.name_transliteration
        }]

    def create(self, validated_data):
        mushaf_uuid = validated_data.pop('mushaf_uuid')
        name = validated_data.pop('name')
        from quran.models import Mushaf
        mushaf = Mushaf.objects.get(uuid=mushaf_uuid)
        validated_data['mushaf'] = mushaf
        validated_data['name'] = name
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)

class SurahInAyahSerializer(serializers.ModelSerializer):
    names = serializers.SerializerMethodField()
    
    class Meta:
        model = Surah
        fields = ['uuid', 'names']
        read_only_fields = ['creator']

    def get_names(self, instance):
        return [{
            'name': instance.name,
            'pronunciation': instance.name_pronunciation,
            'translation': instance.name_translation,
            'transliteration': instance.name_transliteration
        }]

class AyahSerializer(serializers.ModelSerializer):
    text = serializers.SerializerMethodField()
    breakers = serializers.SerializerMethodField()
    bismillah = serializers.SerializerMethodField()
    surah = serializers.SerializerMethodField()
    
    class Meta:
        model = Ayah
        fields = ['uuid', 'number', 'sajdah', 'text', 'breakers', 'bismillah', 'surah']
        read_only_fields = ['creator']
    
    def get_surah(self, instance):
        if instance.number == 1:
            return SurahSerializer(instance.surah).data
        return None

    def get_text(self, instance):
        words = list(instance.words.all().order_by('id'))
        if not words:
            return [] if self.context.get('text_format') == 'word' else ''
            
        if self.context.get('text_format') == 'word':
            # Get all word breakers for these words
            word_ids = [word.id for word in words]
            word_breakers = WordBreaker.objects.filter(word_id__in=word_ids)
            
            # Group breakers by word_id
            breakers_by_word = {}
            for breaker in word_breakers:
                if breaker.word_id not in breakers_by_word:
                    breakers_by_word[breaker.word_id] = []
                breakers_by_word[breaker.word_id].append({
                    'name': breaker.name
                })
            
            # Return words with their breakers (only if they have any)
            result = []
            for word in words:
                word_data = {'text': word.text}
                if word.id in breakers_by_word:
                    word_data['breakers'] = breakers_by_word[word.id]
                result.append(word_data)
            return result
            
        return ' '.join(word.text for word in words)

    def get_breakers(self, instance):
        breakers = instance.breakers.all()
        if not breakers.exists():
            return None
            
        # Get all breakers up to current ayah across all surahs
        current_surah = instance.surah
        current_number = instance.number
        
        all_breakers = AyahBreaker.objects.filter(
            models.Q(
                ayah__surah__number__lt=current_surah.number
            ) | models.Q(
                ayah__surah=current_surah,
                ayah__number__lte=current_number
            )
        ).order_by('ayah__surah__number', 'ayah__number')
        
        # Keep running count of breakers
        breaker_counts = {}
        ayah_breakers = {}
        
        for breaker in all_breakers:
            # Update count for this breaker name
            if breaker.name not in breaker_counts:
                breaker_counts[breaker.name] = 1
            else:
                breaker_counts[breaker.name] += 1
                
            # Store current counts for this ayah
            if breaker.ayah_id not in ayah_breakers:
                ayah_breakers[breaker.ayah_id] = []
            
            # Only add if name not already in this ayah's breakers
            if not any(b['name'] == breaker.name for b in ayah_breakers[breaker.ayah_id]):
                ayah_breakers[breaker.ayah_id].append({
                    'name': breaker.name,
                    'number': breaker_counts[breaker.name]
                })
        
        # Return breakers for current ayah
        return ayah_breakers.get(instance.id, None)

    def get_bismillah(self, instance):
        if not instance.is_bismillah:
            return None
        return {
            'is_ayah': instance.is_bismillah,
            'text': instance.bismillah_text
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Remove null fields safely
        for field in ['breakers', 'sajdah', 'bismillah', 'surah']:
            if field in representation and representation[field] is None:
                representation.pop(field)
        return representation

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)

class WordSerializer(serializers.ModelSerializer):
    ayah_uuid = serializers.UUIDField(write_only=True)

    class Meta:
        model = Word
        fields = ['uuid', 'ayah_uuid', 'text']
        read_only_fields = ['creator']

    def create(self, validated_data):
        from quran.models import Ayah
        ayah_uuid = validated_data.pop('ayah_uuid')
        ayah = Ayah.objects.get(uuid=ayah_uuid)
        validated_data['ayah'] = ayah
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['ayah_uuid'] = str(instance.ayah.uuid)
        return rep

class AyahSerializerView(AyahSerializer):
    surah = SurahInAyahSerializer(read_only=True)
    mushaf = serializers.SerializerMethodField()
    words = WordSerializer(many=True, read_only=True)
    
    class Meta(AyahSerializer.Meta):
        fields = AyahSerializer.Meta.fields + ['surah', 'mushaf', 'words']

    def get_mushaf(self, instance):
        return MushafSerializer(instance.surah.mushaf).data


# Separate serializer for ayahs in surah
class AyahInSurahSerializer(AyahSerializer):
    class Meta(AyahSerializer.Meta):
        fields = ['uuid', 'number', 'sajdah', 'is_bismillah', 'bismillah_text', 'text']
        

class SurahDetailSerializer(SurahSerializer):
    ayahs = AyahInSurahSerializer(many=True, read_only=True)
    
    class Meta(SurahSerializer.Meta):
        fields = SurahSerializer.Meta.fields + ['ayahs']

class AyahTranslationNestedSerializer(serializers.ModelSerializer):
    ayah_uuid = serializers.UUIDField(source='ayah.uuid', read_only=True)
    bismillah = serializers.SerializerMethodField()

    class Meta:
        model = AyahTranslation
        fields = ['uuid', 'ayah_uuid', 'text', 'bismillah']
        read_only_fields = ['creator']

    def get_bismillah(self, obj):
        # Only include bismillah for the first ayah in the surah (ayah number 1)
        if hasattr(obj, 'ayah') and getattr(obj.ayah, 'number', None) == 1:
            return obj.bismillah
        return None

class TranslationSerializer(serializers.ModelSerializer):
    mushaf_uuid = serializers.SerializerMethodField()
    translator_uuid = serializers.SerializerMethodField()

    class Meta:
        model = Translation
        fields = ['uuid', 'mushaf_uuid', 'translator_uuid', 'language', 'release_date', 'source', 'status']
        read_only_fields = ['creator']

    def get_mushaf_uuid(self, obj):
        return str(obj.mushaf.uuid) if obj.mushaf else None

    def get_translator_uuid(self, obj):
        return str(obj.translator.uuid) if obj.translator else None
    def to_internal_value(self, data):
        # Extract UUIDs for input
        mushaf_uuid = data.get('mushaf_uuid')
        translator_uuid = data.get('translator_uuid')
        ret = super().to_internal_value(data)
        ret['mushaf_uuid'] = mushaf_uuid
        ret['translator_uuid'] = translator_uuid
        return ret

    def create(self, validated_data):
        from quran.models import Mushaf
        from account.models import CustomUser
        mushaf_uuid = validated_data.pop('mushaf_uuid')
        translator_uuid = validated_data.pop('translator_uuid')
        mushaf = Mushaf.objects.get(uuid=mushaf_uuid)
        translator = CustomUser.objects.get(uuid=translator_uuid)
        validated_data['mushaf'] = mushaf
        validated_data['translator'] = translator
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['mushaf_uuid'] = str(instance.mushaf.uuid)
        rep['translator_uuid'] = str(instance.translator.uuid)
        return rep

class AyahTranslationSerializer(serializers.ModelSerializer):
    translation_uuid = serializers.UUIDField(write_only=True)
    ayah_uuid = serializers.UUIDField(write_only=True)

    class Meta:
        model = AyahTranslation
        fields = ['uuid', 'translation_uuid', 'ayah_uuid', 'text', 'bismillah']
        read_only_fields = ['creator']

    def create(self, validated_data):
        from quran.models import Translation, Ayah
        translation_uuid = validated_data.pop('translation_uuid')
        ayah_uuid = validated_data.pop('ayah_uuid')
        translation = Translation.objects.get(uuid=translation_uuid)
        ayah = Ayah.objects.get(uuid=ayah_uuid)
        validated_data['translation'] = translation
        validated_data['ayah'] = ayah
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['ayah_uuid'] = str(instance.ayah.uuid)
        return rep

class AyahBreakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AyahBreaker
        fields = ['uuid', 'ayah_id', 'owner_id', 'name']
        read_only_fields = ['creator']

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)

class WordBreakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordBreaker
        fields = ['uuid', 'word_id', 'owner_id', 'name']
        read_only_fields = ['creator']

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)

class AyahAddSerializer(serializers.Serializer):
    surah_uuid = serializers.UUIDField()
    text = serializers.CharField()
    is_bismillah = serializers.BooleanField(default=False)
    bismillah_text = serializers.CharField(required=False, allow_null=True)
    sajdah = serializers.CharField(required=False, allow_null=True)

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'number': instance.number,
            'surah_uuid': str(instance.surah.uuid),
            'is_bismillah': instance.is_bismillah,
            'bismillah_text': instance.bismillah_text,
            'sajdah': instance.sajdah
        }

    def create(self, validated_data):
        # Get the text and remove it from validated_data
        text = validated_data.pop('text')
        surah_uuid = validated_data.pop('surah_uuid')
        
        # Get the surah by uuid
        surah = Surah.objects.get(uuid=surah_uuid)
        
        # Get the latest ayah number in this surah and increment it
        latest_ayah = Ayah.objects.filter(surah=surah).order_by('-number').first()
        next_number = 1 if latest_ayah is None else latest_ayah.number + 1
        
        # Create the ayah
        ayah_data = {
            'surah': surah,
            'creator': self.context['request'].user,
            'number': next_number,
            'is_bismillah': validated_data.get('is_bismillah', False),
            'bismillah_text': validated_data.get('bismillah_text', None),
            'sajdah': validated_data.get('sajdah', None)
        }
        ayah = Ayah.objects.create(**ayah_data)
        
        # Create words from the text
        if text:
            # Split text into words (you might want to use a more sophisticated word splitting logic)
            words = text.split(" ")
            for word_text in words:
                Word.objects.create(
                    ayah=ayah,
                    text=word_text,
                    creator=self.context['request'].user
                )
        
        return ayah

class RecitationSerializer(serializers.ModelSerializer):
    mushaf_uuid = serializers.UUIDField(write_only=True)
    surah_uuid = serializers.UUIDField(write_only=True)
    file = serializers.DictField(write_only=True)
    words_timestamps = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        ),
        required=True,
        write_only=True
    )
    ayahs_timestamps = serializers.SerializerMethodField()
    # Add read-only fields for output
    get_mushaf_uuid = serializers.SerializerMethodField(read_only=True)
    get_surah_uuid = serializers.SerializerMethodField(read_only=True)
    reciter_account_uuid = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recitation
        fields = ['uuid', 'mushaf_uuid', 'get_mushaf_uuid', 'surah_uuid', 'get_surah_uuid', 'status', 'reciter_account_uuid', 'recitation_date', 'recitation_location', 
                 'duration', 'file', 'recitation_type', 'created_at', 'updated_at', 'words_timestamps', 'ayahs_timestamps']
        read_only_fields = ['creator', 'get_mushaf_uuid', 'get_surah_uuid', 'reciter_account_uuid']

    def get_get_mushaf_uuid(self, obj):
        return str(obj.mushaf.uuid) if obj.mushaf else None

    def get_get_surah_uuid(self, obj):
        return str(obj.surah.uuid) if obj.surah else None

    def get_reciter_account_uuid(self, obj):
        return str(obj.reciter_account.uuid) if obj.reciter_account else None

    def to_internal_value(self, data):
        mushaf_uuid = data.get('mushaf_uuid')
        surah_uuid = data.get('surah_uuid')
        ret = super().to_internal_value(data)
        ret['mushaf_uuid'] = mushaf_uuid
        ret['surah_uuid'] = surah_uuid
        return ret

    def create(self, validated_data):
        from quran.models import Mushaf, Surah
        file_data = validated_data.pop('file', None)
        mushaf_uuid = validated_data.pop('mushaf_uuid')
        surah_uuid = validated_data.pop('surah_uuid')
        mushaf = Mushaf.objects.get(uuid=mushaf_uuid)
        surah = Surah.objects.get(uuid=surah_uuid)
        validated_data['mushaf'] = mushaf
        validated_data['surah'] = surah
        if file_data and 's3_uuid' in file_data:
            from quran.models import File
            try:
                file = File.objects.get(s3_uuid=file_data['s3_uuid'])
                validated_data['file_id'] = file.id
            except File.DoesNotExist:
                raise serializers.ValidationError({"file": "File with this s3_uuid does not exist"})
        validated_data['creator'] = self.context['request'].user
        # Accept words_timestamps as the input for timestamps
        timestamps_data = validated_data.pop('words_timestamps', None)
        recitation = super().create(validated_data)
        if timestamps_data:
            from quran.models import Word, RecitationTimestamp
            from datetime import datetime
            for timestamp in timestamps_data:
                try:
                    start_time = datetime.strptime(timestamp['start'], "%H:%M:%S.%f")
                    end_time = datetime.strptime(timestamp['end'], "%H:%M:%S.%f") if timestamp.get('end') else None
                    word = None
                    if timestamp.get('word_uuid'):
                        try:
                            word = Word.objects.get(uuid=timestamp['word_uuid'])
                        except Word.DoesNotExist:
                            continue
                    RecitationTimestamp.objects.create(
                        recitation=recitation,
                        start_time=start_time,
                        end_time=end_time,
                        word=word
                    )
                except (ValueError, KeyError):
                    continue
        return recitation

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Remove write-only fields from output
        representation.pop('mushaf_uuid', None)
        representation.pop('surah_uuid', None)
        # Always show UUIDs using the read-only methods
        representation['mushaf_uuid'] = representation.pop('get_mushaf_uuid', None)
        representation['surah_uuid'] = representation.pop('get_surah_uuid', None)
        # Remove reciter_account (int id) from output if present
        representation.pop('reciter_account', None)

        # Dynamic timestamp field logic
        action = self.context.get('view').action if self.context.get('view') else None
        request = self.context.get('request')
        if request and request.query_params.get('words_timestamps', 'true').lower() == 'false' and action == "retrieve":
            representation.pop('words_timestamps', None)
        else:
            representation['words_timestamps'] = self.get_words_timestamps(instance)

        if action == 'list':
            representation.pop('words_timestamps', None)
            representation.pop('ayahs_timestamps', None)

        return representation

    def get_ayahs_timestamps(self, obj):
        # Get all timestamps ordered by start time
        timestamps = obj.timestamps.all().order_by('start_time')
        ayahs = Ayah.objects.filter(surah=obj.surah).all()
        ayahs_first_words_as_id = set()
        for ayah in ayahs:
            words_with_id = ayah.words.values("id").first()
            ayahs_first_words_as_id.add(words_with_id['id'])

        if not timestamps:
            return []
        
        # Skip the first ayah and get start times of remaining ayahs
        ayah_start_times = []
        for timestamp in timestamps[1:]:  # Skip first timestamp
            start_time = timestamp.start_time.strftime('%H:%M:%S.%f')[:-3]  # Remove last 3 digits of microseconds
            if timestamp.word_id in ayahs_first_words_as_id:
                ayah_start_times.append(start_time)
        return ayah_start_times

    def validate_timestamps(self, value):
        if not value:
            raise serializers.ValidationError("Timestamps are required")
        return value

    def get_file(self, obj):
        return f"{settings.AWS_S3_ENDPOINT_URL}/{settings.AWS_STORAGE_BUCKET_NAME}/{settings.LOCATION_PREFIX}recitations/{obj.file.s3_uuid}.{obj.file.format}"

    def get_words_timestamps(self, obj):
        timestamps = []
        for timestamp in obj.timestamps.all():
            # Format the time as HH:MM:SS.mmm
            start_time = timestamp.start_time.strftime('%H:%M:%S.%f')[:-3]  # Remove last 3 digits of microseconds
            end_time = timestamp.end_time.strftime('%H:%M:%S.%f')[:-3] if timestamp.end_time else None
            
            timestamps.append({
                'start': start_time,
                'end': end_time,
                'word_uuid': str(timestamp.word.uuid) if timestamp.word else None
            })
        return timestamps

class TranslationListSerializer(serializers.ModelSerializer):
    mushaf_uuid = serializers.SerializerMethodField()
    translator_uuid = serializers.SerializerMethodField()

    class Meta:
        model = Translation
        fields = ['uuid', 'mushaf_uuid', 'translator_uuid', 'language', 'release_date', 'source', 'status']
        read_only_fields = ['creator']

    def get_mushaf_uuid(self, obj):
        return str(obj.mushaf.uuid) if obj.mushaf else None

    def get_translator_uuid(self, obj):
        return str(obj.translator.uuid) if obj.translator else None
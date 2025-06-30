from rest_framework import serializers
from django.db import models
from datetime import datetime
from django.conf import settings

from quran.models import Mushaf, Surah, Ayah, Word, Translation, AyahTranslation, AyahBreaker, WordBreaker, Recitation, File, RecitationTimestamp, Status

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
            'name_pronunciation': instance.name_pronunciation,
            'name_translation': instance.name_translation,
            'name_transliteration': instance.name_transliteration
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
            'name_pronunciation': instance.name_pronunciation,
            'name_translation': instance.name_translation,
            'name_transliteration': instance.name_transliteration
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
        # Remove null fields
        if representation['breakers'] is None:
            representation.pop('breakers')
        if representation['sajdah'] is None:
            representation.pop('sajdah')
        if representation['bismillah'] is None:
            representation.pop('bismillah')
        if representation['surah'] is None:
            representation.pop('surah')
        return representation

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)

class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = ['uuid', 'ayah_id', 'text']
        read_only_fields = ['creator']

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)

class AyahSerializerView(AyahSerializer):
    surah = SurahInAyahSerializer(read_only=True)
    mushaf = serializers.SerializerMethodField()
    words = WordSerializer(many=True, read_only=True)
    
    class Meta(AyahSerializer.Meta):
        fields = AyahSerializer.Meta.fields + ['surah', 'mushaf', 'words']

    def get_mushaf(self, instance):
        return MushafSerializer(instance.surah.mushaf).data

class SurahDetailSerializer(SurahSerializer):
    ayahs = AyahSerializer(many=True, read_only=True)
    
    class Meta(SurahSerializer.Meta):
        fields = SurahSerializer.Meta.fields + ['ayahs']

class TranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Translation
        fields = ['uuid', 'mushaf', 'translator', 'language', 'release_date', 'source', 'status']
        read_only_fields = ['creator']

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)

class AyahTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AyahTranslation
        fields = ['uuid', 'translation_id', 'ayah_id', 'text', 'bismillah']
        read_only_fields = ['creator']

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)

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
    surah_id = serializers.IntegerField()
    text = serializers.CharField()
    is_bismillah = serializers.BooleanField(default=False)
    bismillah_text = serializers.CharField(required=False, allow_null=True)
    sajdah = serializers.CharField(required=False, allow_null=True)

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'number': instance.number,
            'surah_id': instance.surah.id,
            'is_bismillah': instance.is_bismillah,
            'bismillah_text': instance.bismillah_text,
            'sajdah': instance.sajdah
        }

    def create(self, validated_data):
        # Get the text and remove it from validated_data
        text = validated_data.pop('text')
        surah_id = validated_data.pop('surah_id')
        
        # Get the surah
        surah = Surah.objects.get(id=surah_id)
        
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
    file = serializers.DictField(write_only=True)
    words_timestamps = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        ),
        required=True,
        write_only=True
    )
    ayahs_timestamps = serializers.SerializerMethodField()

    class Meta:
        model = Recitation
        fields = ['uuid', 'mushaf', 'surah', 'status', 'reciter_account', 'recitation_date', 'recitation_location', 
                 'duration', 'file', 'recitation_type', 'created_at', 'updated_at', 'words_timestamps', 'ayahs_timestamps']
        read_only_fields = ['creator']

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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        action = self.context.get('view').action
        # Check if timestamps should be included in response
        request = self.context.get('request')
        if request and request.query_params.get('words_timestamps', 'true').lower() == 'false' and action == "retrieve":
            representation.pop('words_timestamps', None)
        else:
            representation['words_timestamps'] = self.get_words_timestamps(instance)
        
        if action == 'list':
            representation.pop('words_timestamps', None)
            representation.pop('ayahs_timestamps', None)
            
        return representation

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

    def create(self, validated_data):
        file_data = validated_data.pop('file', None)
        
        # Get file from s3_uuid
        if file_data and 's3_uuid' in file_data:
            try:
                file = File.objects.get(s3_uuid=file_data['s3_uuid'])
                validated_data['file_id'] = file.id
            except File.DoesNotExist:
                raise serializers.ValidationError({"file": "File with this s3_uuid does not exist"})
        
        validated_data['creator'] = self.context['request'].user
        
        # Remove timestamps from validated_data as it's not a model field
        timestamps_data = validated_data.pop('timestamps', None)
        
        # Create the recitation
        recitation = super().create(validated_data)
        
        # Create timestamps if provided
        if timestamps_data:
            for timestamp in timestamps_data:
                try:
                    start_time = datetime.strptime(timestamp['start'], "%H:%M:%S.%f")
                    end_time = datetime.strptime(timestamp['end'], "%H:%M:%S.%f") if timestamp.get('end') else None
                    
                    # Get word if word_uuid is provided
                    word = None
                    if timestamp.get('word_uuid'):
                        try:
                            word = Word.objects.get(uuid=timestamp['word_uuid'])
                        except Word.DoesNotExist:
                            continue
                    
                    # Create timestamp
                    RecitationTimestamp.objects.create(
                        recitation=recitation,
                        start_time=start_time,
                        end_time=end_time,
                        word=word
                    )
                except (ValueError, KeyError) as e:
                    continue
        
        return recitation
from rest_framework import serializers
from django.core.validators import RegexValidator
from django.db import models

from quran.models import Mushaf, Surah, Ayah, Word, Translation, AyahTranslation, AyahBreaker, WordBreaker

class MushafSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mushaf
        fields = ['id', 'short_name', 'name', 'source']
        read_only_fields = ['creator']

    def create(self, validated_data):
        return Mushaf.objects.create(**validated_data)

class SurahNameSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50)
    name_pronunciation = serializers.CharField(required=False, allow_null=True)
    name_translation = serializers.CharField(required=False, allow_null=True)
    name_transliteration = serializers.CharField(required=False, allow_null=True)

class SurahSerializer(serializers.ModelSerializer):
    names = serializers.SerializerMethodField()
    mushaf = MushafSerializer(read_only=True)
    
    class Meta:
        model = Surah
        fields = ['id', 'mushaf', 'names', 'number', 'period', 'search_terms']
        read_only_fields = ['creator']

    def get_names(self, instance):
        return [{
            'name': instance.name,
            'name_pronunciation': instance.name_pronunciation,
            'name_translation': instance.name_translation,
            'name_transliteration': instance.name_transliteration
        }]

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)

class SurahInAyahSerializer(serializers.ModelSerializer):
    names = serializers.SerializerMethodField()
    
    class Meta:
        model = Surah
        fields = ['id', 'names']
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
    
    class Meta:
        model = Ayah
        fields = ['id', 'number', 'sajdah', 'text', 'breakers', 'bismillah']
        read_only_fields = ['creator']

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
        return representation

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)

class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = ['id', 'ayah_id', 'text']
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
        fields = ['id', 'mushaf', 'translator', 'language', 'release_date', 'source', 'approved']
        read_only_fields = ['creator']

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)

class AyahTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AyahTranslation
        fields = ['id', 'translation_id', 'ayah_id', 'text', 'bismillah']
        read_only_fields = ['creator']

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)

class AyahBreakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AyahBreaker
        fields = ['id', 'ayah_id', 'owner_id', 'name']
        read_only_fields = ['creator']

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)

class WordBreakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordBreaker
        fields = ['id', 'word_id', 'owner_id', 'name']
        read_only_fields = ['creator']

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)

class AyahAddSerializer(serializers.ModelSerializer):
    surah_uuid = serializers.UUIDField()
    text = serializers.CharField()
    is_bismillah = serializers.BooleanField(default=False)
    bismillah_text = serializers.CharField(required=False, allow_null=True)
    sajdah = serializers.CharField(required=False, allow_null=True)
    
    class Meta:
        model = Ayah
        fields = ['surah_uuid', 'text', 'is_bismillah', 'bismillah_text', 'sajdah']
        read_only_fields = ['creator']

    def create(self, validated_data):
        # Get the text and remove it from validated_data
        text = validated_data.pop('text')
        surah_uuid = validated_data.pop('surah_uuid')
        
        # Get the surah
        surah = Surah.objects.get(id=surah_uuid)
        
        # Create the ayah
        validated_data['surah'] = surah
        validated_data['creator'] = self.context['request'].user
        ayah = super().create(validated_data)
        
        # Create words from the text
        if text:
            # Split text into words (you might want to use a more sophisticated word splitting logic)
            words = text.split()
            for word_text in words:
                Word.objects.create(
                    ayah=ayah,
                    text=word_text,
                    creator=self.context['request'].user
                )
        
        return ayah
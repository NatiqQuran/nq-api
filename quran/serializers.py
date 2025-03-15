from rest_framework import serializers
from django.core.validators import RegexValidator
from django.db import models

from quran.models import Mushaf, Surah, Ayah, Word, Translation, AyahTranslation, AyahBreaker, WordBreaker

class MushafSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    short_name = serializers.CharField(
        required=True,
        max_length=100,
        validators=[RegexValidator(
            regex='^[a-zA-Z]*$',
            message='Short name must contain only alphabetic characters',
            code='invalid_short_name'
        )]
    )
    name = serializers.CharField(required=True)
    source = serializers.CharField(required=True)

    def create(self, validated_data):
        return Mushaf.objects.create(**validated_data)

class SurahSerializer(serializers.ModelSerializer):
    class Meta:
        model = Surah
        fields = ['id', 'mushaf', 'name', 'number', 'period', 'name_pronunciation', 
                 'name_translation', 'name_transliteration', 'search_terms']
        read_only_fields = ['creator']

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)

class AyahSerializer(serializers.ModelSerializer):
    text = serializers.SerializerMethodField()
    breakers = serializers.SerializerMethodField()
    
    class Meta:
        model = Ayah
        fields = ['id', 'surah', 'number', 'sajdah', 'is_bismillah', 'bismillah_text', 'text', 'breakers']
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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if representation['breakers'] is None:
            representation.pop('breakers')
        return representation

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)

class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = ['id', 'ayah', 'text']
        read_only_fields = ['creator']

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)

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
        fields = ['id', 'translation', 'ayah', 'text', 'bismillah']
        read_only_fields = ['creator']

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)

class AyahBreakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AyahBreaker
        fields = ['id', 'ayah', 'owner', 'name']
        read_only_fields = ['creator']

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)

class WordBreakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordBreaker
        fields = ['id', 'word', 'owner', 'name']
        read_only_fields = ['creator']

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)
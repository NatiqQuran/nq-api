from rest_framework import serializers
from django.core.validators import RegexValidator

from quran.models import Mushaf, Surah, Ayah, Word, Translation, AyahTranslation

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
    
    class Meta:
        model = Ayah
        fields = ['id', 'surah', 'number', 'sajdah', 'is_bismillah', 'bismillah_text', 'text']
        read_only_fields = ['creator']

    def get_text(self, instance):
        print("OK")
        words = list(instance.words.all().order_by('id'))
        if not words:
            return [] if self.context.get('text_format') == 'word' else ''
            
        if self.context.get('text_format') == 'word':
            return [word.text for word in words]
        return ' '.join(word.text for word in words)

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
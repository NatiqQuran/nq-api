from rest_framework import serializers
from django.core.validators import RegexValidator
from django.db import models

from core.models import ErrorLogs, PhraseTranslations, Phrases

class ErrorLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErrorLogs
        fields = '__all__'

class PhraseTranslationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhraseTranslations
        fields = ['id', 'phrase', 'text', 'language']
        read_only_fields = ['creator']
        
    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)
    

class PhrasesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phrases
        fields = ['id', 'phrase', 'translations']
        read_only_fields = ['creator']

    def get_translations(self, instance):
        translations = PhraseTranslations.objects.filter(phrase=instance)
        return PhraseTranslationsSerializer(translations, many=True).data

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)
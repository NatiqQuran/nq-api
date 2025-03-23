from rest_framework import serializers
from django.core.validators import RegexValidator
from django.db import models

from core.models import ErrorLog, PhraseTranslation, Phrase

class ErrorLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErrorLog
        fields = '__all__'

class PhraseTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhraseTranslation
        fields = ['id', 'phrase', 'text', 'language']
        read_only_fields = ['creator']
        
    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)
    

class PhraseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phrase
        fields = ['id', 'phrase',]
        read_only_fields = ['creator']

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)
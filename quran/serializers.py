from rest_framework import serializers
from django.core.validators import RegexValidator

from quran.models import Mushaf

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
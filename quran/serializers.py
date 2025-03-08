from rest_framework import serializers

from quran.models import Mushaf

class MushafSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    short_name = serializers.CharField(required=True, max_length=100)
    name = serializers.CharField(required=True)
    source = serializers.CharField(required=True)

    def create(self, validated_data):
        return Mushaf.objects.create(**validated_data)
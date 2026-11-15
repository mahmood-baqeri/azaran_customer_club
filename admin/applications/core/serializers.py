from rest_framework import serializers


class TinyMCEUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
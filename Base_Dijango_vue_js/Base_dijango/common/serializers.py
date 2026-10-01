from rest_framework import serializers


class ApiErrorSerializer(serializers.Serializer):
    code = serializers.CharField(read_only=True)
    message = serializers.CharField(read_only=True)
    details = serializers.DictField(read_only=True)
    request_id = serializers.CharField(read_only=True)

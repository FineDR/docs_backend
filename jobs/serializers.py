from rest_framework import serializers

class JobSerializer(serializers.Serializer):
    source = serializers.CharField()
    title = serializers.CharField()
    company = serializers.CharField(allow_blank=True, required=False)
    location = serializers.CharField(allow_blank=True, required=False)
    link = serializers.URLField()
    date_posted = serializers.DateTimeField(required=False, allow_null=True)

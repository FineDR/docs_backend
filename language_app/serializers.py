from rest_framework import serializers
from .models import Language

class LanguageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)  # optional for updates

    class Meta:
        model = Language
        fields = ["id", "language", "proficiency"]

    def create(self, validated_data):
        user = self.context["request"].user
        return Language.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

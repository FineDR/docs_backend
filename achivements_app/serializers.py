from rest_framework import serializers
from .models import AchievementProfile, Achievement

class AchievementSerializer(serializers.ModelSerializer):
    profile = serializers.PrimaryKeyRelatedField(
        read_only=True,  # profile is assigned automatically from user
        source='profile.id'
    )

    class Meta:
        model = Achievement
        fields = ["id", "value", "profile"]  # match frontend interface

class AchievementProfileSerializer(serializers.ModelSerializer):
    # Keep for full profile retrieval
    achievements = AchievementSerializer(many=True, read_only=True)

    class Meta:
        model = AchievementProfile
        fields = ["full_name", "email", "achievements"]

    def create(self, validated_data):
        user = self.context["request"].user
        profile, _ = AchievementProfile.objects.get_or_create(
            user=user,
            defaults={
                "full_name": validated_data.get("full_name"),
                "email": validated_data.get("email"),
            },
        )
        return profile

    def update(self, instance, validated_data):
        instance.full_name = validated_data.get("full_name", instance.full_name)
        instance.email = validated_data.get("email", instance.email)
        instance.save()
        return instance

# serializers.py
from rest_framework import serializers
from .models import AchievementProfile, Achievement

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ["id", "value"]   # include id so frontend can update/delete

class AchievementProfileSerializer(serializers.ModelSerializer):
    achievements = AchievementSerializer(many=True)  # match related_name

    class Meta:
        model = AchievementProfile
        fields = ["full_name", "email", "achievements"]

    def create(self, validated_data):
        """
        Append new achievements (do not delete existing ones)
        """
        achievements_data = validated_data.pop("achievements", [])
        user = self.context["request"].user

        profile, _ = AchievementProfile.objects.get_or_create(
            user=user,
            defaults={
                "full_name": validated_data.get("full_name"),
                "email": validated_data.get("email"),
            },
        )

        # ✅ Append new achievements (no deletion)
        for ach_data in achievements_data:
            Achievement.objects.create(profile=profile, **ach_data)

        return profile

    def update(self, instance, validated_data):
        """
        Replace all achievements (delete old ones first)
        """
        achievements_data = validated_data.pop("achievements", [])
        instance.full_name = validated_data.get("full_name", instance.full_name)
        instance.email = validated_data.get("email", instance.email)
        instance.save()

        # ✅ Replace mode — clear all and recreate
        instance.achievements.all().delete()
        for ach_data in achievements_data:
            Achievement.objects.create(profile=instance, **ach_data)

        return instance

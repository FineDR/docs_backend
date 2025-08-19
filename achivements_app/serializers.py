from rest_framework import serializers
from .models import AchievementProfile, Achievement

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['value']

class AchievementProfileSerializer(serializers.ModelSerializer):
    # This must match the related_name in Achievement model
    achievement = AchievementSerializer(many=True)

    class Meta:
        model = AchievementProfile
        fields = ['full_name', 'email', 'achievement']

    def create(self, validated_data):
        achievements_data = validated_data.pop('achievement', [])
        user = self.context['request'].user
        profile, _ = AchievementProfile.objects.get_or_create(
            user=user,
            defaults={'full_name': validated_data.get('full_name'), 'email': validated_data.get('email')}
        )

        # Clear existing achievements if updating
        profile.achievements.all().delete()

        # Create new achievements
        for ach_data in achievements_data:
            Achievement.objects.create(profile=profile, **ach_data)

        return profile

    def update(self, instance, validated_data):
        achievements_data = validated_data.pop('achievement', [])
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        if achievements_data:
            instance.achievements.all().delete()
            for ach_data in achievements_data:
                Achievement.objects.create(profile=instance, **ach_data)

        return instance

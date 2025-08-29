from rest_framework import serializers
from .models import SkillSet, TechnicalSkill, SoftSkill

class TechnicalSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnicalSkill
        fields = ['id', 'value']


class SoftSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoftSkill
        fields = ['id', 'value']


class SkillSetSerializer(serializers.ModelSerializer):
    technicalSkills = TechnicalSkillSerializer(many=True, source='technical_skills')
    softSkills = SoftSkillSerializer(many=True, source='soft_skills')

    class Meta:
        model = SkillSet
        fields = ['id', 'full_name', 'email', 'technicalSkills', 'softSkills']

    def create(self, validated_data):
        technical_data = validated_data.pop('technical_skills', [])
        soft_data = validated_data.pop('soft_skills', [])
        user = self.context['request'].user

        skill_set = SkillSet.objects.create(user=user, **validated_data)

        for tech in technical_data:
            TechnicalSkill.objects.create(skill_set=skill_set, **tech)
        for soft in soft_data:
            SoftSkill.objects.create(skill_set=skill_set, **soft)

        return skill_set

    def update(self, instance, validated_data):
        technical_data = validated_data.pop('technical_skills', [])
        soft_data = validated_data.pop('soft_skills', [])

        # ✅ Update basic fields
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        # ✅ Clear and recreate technical skills
        instance.technical_skills.all().delete()
        for tech in technical_data:
            TechnicalSkill.objects.create(skill_set=instance, **tech)

        # ✅ Clear and recreate soft skills
        instance.soft_skills.all().delete()
        for soft in soft_data:
            SoftSkill.objects.create(skill_set=instance, **soft)

        return instance  # ✅ MUST RETURN

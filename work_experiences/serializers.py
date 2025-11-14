# serializers.py
from rest_framework import serializers
from .models import WorkExperience, Responsibility

class ResponsibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Responsibility
        fields = ["value"]

class WorkExperienceSerializer(serializers.ModelSerializer):
    responsibilities = ResponsibilitySerializer(many=True)

    class Meta:
        model = WorkExperience
        fields = ["id", "job_title", "company", "location", "start_date", "end_date", "responsibilities"]

    def create(self, validated_data):
        responsibilities_data = validated_data.pop("responsibilities", [])
        user = self.context["request"].user
        work_experience = WorkExperience.objects.create(user=user, **validated_data)

        for resp_data in responsibilities_data:
            Responsibility.objects.create(work_experience=work_experience, **resp_data)

        return work_experience

    def update(self, instance, validated_data):
        responsibilities_data = validated_data.pop("responsibilities", [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Replace responsibilities
        instance.responsibilities.all().delete()
        for resp_data in responsibilities_data:
            Responsibility.objects.create(work_experience=instance, **resp_data)

        return instance

class WorkExperienceListSerializer(serializers.ListSerializer):
    child = WorkExperienceSerializer()  # Each item uses the normal serializer

    def create(self, validated_data):
        experiences = []
        user = self.context["request"].user
        for exp_data in validated_data:
            responsibilities_data = exp_data.pop("responsibilities", [])
            work_experience = WorkExperience.objects.create(user=user, **exp_data)
            for resp_data in responsibilities_data:
                Responsibility.objects.create(work_experience=work_experience, **resp_data)
            experiences.append(work_experience)
        return experiences

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
        user = self.context["request"].user  # get the logged-in user

        work_experience = WorkExperience.objects.create(user=user, **validated_data)

        for resp_data in responsibilities_data:
            Responsibility.objects.create(work_experience=work_experience, **resp_data)

        return work_experience

    def update(self, instance, validated_data):
        responsibilities_data = validated_data.pop("responsibilities", [])
        instance.job_title = validated_data.get("job_title", instance.job_title)
        instance.company = validated_data.get("company", instance.company)
        instance.location = validated_data.get("location", instance.location)
        instance.start_date = validated_data.get("start_date", instance.start_date)
        instance.end_date = validated_data.get("end_date", instance.end_date)
        instance.save()

        # Replace old responsibilities with new ones
        instance.responsibilities.all().delete()
        for resp_data in responsibilities_data:
            Responsibility.objects.create(work_experience=instance, **resp_data)

        return instance

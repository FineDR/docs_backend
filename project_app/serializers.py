# serializers.py
from rest_framework import serializers
from .models import Project, Technology

class TechnologySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Technology
        fields = ["id", "value"]

class ProjectSerializer(serializers.ModelSerializer):
    technologies = TechnologySerializer(many=True, required=False)

    class Meta:
        model = Project
        fields = ["id", "title", "description", "link", "technologies", "created_at", "updated_at"]

    def create(self, validated_data):
        technologies_data = validated_data.pop("technologies", [])
        user = self.context["request"].user  # set the user
        project = Project.objects.create(user=user, **validated_data)
        for tech_data in technologies_data:
            Technology.objects.create(project=project, **tech_data)
        return project

    def update(self, instance, validated_data):
        technologies_data = validated_data.pop("technologies", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if technologies_data is not None:
            # Remove old technologies and recreate
            instance.technologies.all().delete()
            for tech_data in technologies_data:
                Technology.objects.create(project=instance, **tech_data)

        return instance

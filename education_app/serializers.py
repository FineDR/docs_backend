from rest_framework import serializers
from .models import Education

class EducationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)  # keep read-only

    class Meta:
        model = Education
        fields = ['id', 'degree', 'institution', 'location', 'start_date', 'end_date', 'grade', 'user']

    def create(self, validated_data):
        # inject authenticated user
        user = self.context['request'].user
        return Education.objects.create(user=user, **validated_data)

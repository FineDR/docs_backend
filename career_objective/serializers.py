from rest_framework import serializers
from .models import CareerObjective

class CareerObjectiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareerObjective
        fields = ["id", "career_objective", "user", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

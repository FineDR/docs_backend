# career_objective/serializers.py
from rest_framework import serializers
from .models import CareerObjective

class CareerObjectiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareerObjective
        fields = ["career_objective"]

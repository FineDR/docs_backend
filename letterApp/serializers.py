from rest_framework import serializers # type: ignore
from .models import Letter

class LetterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Letter
        fields = "__all__"
        read_only_fields = ["user", "created_at"]

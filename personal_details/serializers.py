from rest_framework import serializers
from .models import PersonalDetail

class PersonalDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = PersonalDetail
        fields = [
            'full_name', 'email', 'phone', 'address', 'linkedin',
            'github', 'website', 'date_of_birth', 'nationality', 'profile_summary'
        ]

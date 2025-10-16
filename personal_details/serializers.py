from rest_framework import serializers
from .models import PersonalDetail

class PersonalDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    profile_image = serializers.ImageField(use_url=True, allow_null=True, required=False)

    class Meta:
        model = PersonalDetail
        fields = [
            'full_name', 'email', 'phone', 'address', 'linkedin',
            'github', 'website', 'date_of_birth', 'nationality', 
            'profile_summary', 'profile_image'
        ]

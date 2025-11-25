from rest_framework import serializers
from .models import PersonalDetail

class PersonalDetailSerializer(serializers.ModelSerializer):
    # Use the fields from PersonalDetail instead of the User model
    full_name = serializers.SerializerMethodField(read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    profile_image = serializers.ImageField(use_url=True, allow_null=True, required=False)

    class Meta:
        model = PersonalDetail
        fields = [
            'first_name', 'middle_name', 'last_name', 'full_name', 'email',
            'phone', 'address', 'linkedin', 'github', 'website',
            'date_of_birth', 'nationality', 'profile_summary', 'profile_image'
        ]

    def get_full_name(self, obj):
        return " ".join(filter(None, [obj.first_name, obj.middle_name, obj.last_name]))

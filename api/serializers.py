from rest_framework import serializers
from .models import UserTB
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from career_objective.models import CareerObjective
from achivements_app.models import AchievementProfile,Achievement
from personal_details.models import PersonalDetail
from certificate_app.models import Profile, Certificate
from education_app.models import Education
from language_app.models import Language
from project_app.models import Project,Technology
from skills_app.models import SkillSet,SoftSkill,TechnicalSkill
from work_experiences.models import WorkExperience,Responsibility
from references_app.models import Reference
class CareerObjectiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareerObjective
        fields = "__all__"


class ReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        fields = "__all__"
class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = "__all__"


class AchievementProfileSerializer(serializers.ModelSerializer):
    achievements = AchievementSerializer(many=True, read_only=True)

    class Meta:
        model = AchievementProfile
        fields = "__all__"

class PersonalDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalDetail
        fields = "__all__"


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = "__all__"


class ProfileSerializer(serializers.ModelSerializer):
    certificates = CertificateSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = "__all__"


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = "__all__"


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = "__all__"


class SoftSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoftSkill
        fields = "__all__"


class TechnicalSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnicalSkill
        fields = "__all__"


class SkillSetSerializer(serializers.ModelSerializer):
    soft_skills = SoftSkillSerializer(many=True, read_only=True)
    technical_skills = TechnicalSkillSerializer(many=True, read_only=True)

    class Meta:
        model = SkillSet
        fields = "__all__"


class TechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = Technology
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    technologies = TechnologySerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = "__all__"


class ResponsibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Responsibility
        fields = "__all__"


class WorkExperienceSerializer(serializers.ModelSerializer):
    responsibilities = ResponsibilitySerializer(many=True, read_only=True)

    class Meta:
        model = WorkExperience
        fields = "__all__"


class UserDetailSerializer(serializers.ModelSerializer):
    career_objectives = CareerObjectiveSerializer(many=True, read_only=True)
    achievement_profile = AchievementProfileSerializer(  # 👈 singular
        read_only=True
    )
    personal_details = PersonalDetailSerializer(
        read_only=True, source='personal_detail'
    )
    profiles = ProfileSerializer(read_only=True, source='profile')
    educations = EducationSerializer(many=True, read_only=True)
    languages = LanguageSerializer(many=True, read_only=True)
    skill_sets = SkillSetSerializer(many=True, read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)
    work_experiences = WorkExperienceSerializer(many=True, read_only=True)
    references = ReferenceSerializer(many=True, read_only=True)
    
    class Meta:
        model = UserTB
        exclude = ['password']
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # If enhanced data is provided in the context, use it
        if 'enhanced_data' in self.context:
            enhanced_data = self.context['enhanced_data']
            for key, value in enhanced_data.items():
                if key in representation:
                    representation[key] = value
        
        return representation

class UserTBSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = UserTB
        fields = ["email", "first_name", "middle_name", "last_name", "password", "confirm_password"]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate_email(self, value):
        if UserTB.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered. Please log in.")
        return value

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("confirm_password"):
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        password = validated_data.pop("password")
        user = UserTB(**validated_data)
        user.set_password(password)
        user.is_active = False
        user.save()
        return user



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        user = authenticate(email=email, password=password)
        
        if user is None:
            raise serializers.ValidationError("Invalid credentials")
        if not user.is_active:
            raise serializers.ValidationError("Email not verified. Please check your email.")
        
        data["user"] = user
        return data

class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserTB
        fields = ["email","first_name","middle_name","last_name" ,"is_active"]
        read_only_fields = ["email", "is_active"]



class PasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)

    def validate_new_password(self, value):
        try:
            validate_password(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return value
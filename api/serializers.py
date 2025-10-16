from rest_framework import serializers
from .models import UserTB
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from career_objective.models import CareerObjective
from achivements_app.models import AchievementProfile, Achievement
from personal_details.models import PersonalDetail
from certificate_app.models import Profile, Certificate
from education_app.models import Education
from language_app.models import Language
from project_app.models import Project, Technology
from skills_app.models import SkillSet, SoftSkill, TechnicalSkill
from work_experiences.models import WorkExperience, Responsibility
from references_app.models import Reference
from api.services.ai_service import enhance_cv_data

# ------------------- Nested Serializers -------------------

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


# ------------------- User Detail Serializer -------------------

class UserDetailSerializer(serializers.ModelSerializer):
    career_objectives = CareerObjectiveSerializer(many=True, read_only=True)
    achievement_profile = AchievementProfileSerializer(read_only=True)
    personal_details = PersonalDetailSerializer(read_only=True, source='personal_detail')
    profile = ProfileSerializer(read_only=True)
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
    data = super().to_representation(instance)

    # Helper to format phone numbers consistently
    def format_phone(phone):
        if not phone:
            return ""
        phone = phone.replace(" ", "").replace("+", "")
        if phone.startswith("255"):
            return "+255 " + " ".join([phone[3:6], phone[6:9], phone[9:]])
        return phone

    # Flatten and convert the CV to the target structure
    cv = {
        "id": int(instance.id),
        "full_name": f"{instance.first_name} {instance.middle_name} {instance.last_name}".title(),
        "first_name": instance.first_name.title(),
        "middle_name": instance.middle_name.title(),
        "last_name": instance.last_name.title(),
        "email": instance.email,
        "phone": format_phone(data.get("personal_details", {}).get("phone", "")),
        "address": data.get("personal_details", {}).get("address", "").replace(",", ", "),
        "website": data.get("personal_details", {}).get("website", ""),
        "linkedin": data.get("personal_details", {}).get("linkedin", ""),
        "github": data.get("personal_details", {}).get("github", ""),
        "nationality": data.get("personal_details", {}).get("nationality", ""),
        "date_of_birth": data.get("personal_details", {}).get("date_of_birth", ""),
        "profile_summary": data.get("personal_details", {}).get("profile_summary", ""),
        "career_objective": data.get("career_objectives")[0]["career_objective"]
                            if data.get("career_objectives") else "",

        "educations": [
            {
                "degree": e["degree"],
                "institution": e["institution"],
                "start_date": e["start_date"],
                "end_date": e["end_date"],
                "grade": e["grade"],
                "location": e["location"].replace(",", ", ")
            } for e in data.get("educations", [])
        ],

        "certificates": [
            {
                "name": c["name"],
                "issuer": c["issuer"],
                "date": c["date"]
            } for c in data.get("profile", {}).get("certificates", [])
        ],

        "work_experiences": [
            {
                "company": w["company"],
                "location": w["location"].replace(",", ", "),
                "job_title": w["job_title"].title(),
                "start_date": w["start_date"],
                "end_date": w["end_date"],
                "responsibilities": [
                    r["value"].rstrip(".").capitalize() + "." for r in w.get("responsibilities", [])
                ]
            } for w in data.get("work_experiences", [])
        ],

        "projects": [
            {
                "title": p["title"],
                "description": p["description"],
                "link": p.get("link", ""),
                "technologies": [t["value"] for t in p.get("technologies", [])]
            } for p in data.get("projects", [])
        ],

        "technical_skills": [
            t["value"] for s in data.get("skill_sets", []) for t in s.get("technical_skills", [])
        ],

        "soft_skills": [
            s["value"] for s in data.get("skill_sets", []) for s in s.get("soft_skills", [])
        ],

        "achievements": [
            a["value"].rstrip(".").capitalize() + "." for a in data.get("achievement_profile", {}).get("achievements", [])
        ],

        "languages": [
            {"language": l["language"], "proficiency": l["proficiency"]}
            for l in data.get("languages", [])
        ],

        "references": [
            {
                "name": r["name"],
                "position": r.get("position", ""),
                "email": r.get("email", ""),
                "phone": format_phone(r.get("phone", ""))
            } for r in data.get("references", [])
        ]
    }

    # Make enhanced_data equal to the flattened CV
    data["enhanced_data"] = cv

    return cv


# ------------------- User Registration Serializer -------------------

class UserTBSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True)
    enhanced_data = serializers.JSONField(default=dict)  # Always a dict

    class Meta:
        model = UserTB
        fields = ["email", "first_name", "middle_name", "last_name", "password", "enhanced_data", "confirm_password"]
        extra_kwargs = {"password": {"write_only": True}}

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
        enhanced_data = validated_data.pop("enhanced_data", {}) or {}
        user = UserTB(**validated_data)
        user.set_password(password)
        user.enhanced_data = enhanced_data
        user.is_active = False
        user.save()
        return user


# ------------------- Login Serializer -------------------

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


# ------------------- User Profile Serializer -------------------

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTB
        fields = ["email", "first_name", "middle_name", "last_name", "is_active"]
        read_only_fields = ["email", "is_active"]


# ------------------- Password Reset Serializer -------------------

class PasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)

    def validate_new_password(self, value):
        try:
            validate_password(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return value

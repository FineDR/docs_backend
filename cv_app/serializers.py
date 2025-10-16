from rest_framework import serializers
from .models import UserTB
from career_objective.models import CareerObjective
from achivements_app.models import AchievementProfile, Achievement
from personal_details.models import PersonalDetail
from certificate_app.models import Certificate
from education_app.models import Education
from language_app.models import Language
from project_app.models import Project, Technology
from skills_app.models import SoftSkill, TechnicalSkill
from work_experiences.models import WorkExperience, Responsibility
from references_app.models import Reference


class UserCVSerializer(serializers.ModelSerializer):
    # Derived or nested fields
    full_name = serializers.SerializerMethodField()
    profile_summary = serializers.SerializerMethodField()
    career_objective = serializers.SerializerMethodField()
    educations = serializers.SerializerMethodField()
    certificates = serializers.SerializerMethodField()
    work_experiences = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()
    technical_skills = serializers.SerializerMethodField()
    soft_skills = serializers.SerializerMethodField()
    achievements = serializers.SerializerMethodField()
    languages = serializers.SerializerMethodField()
    references = serializers.SerializerMethodField()

    class Meta:
        model = UserTB
        fields = [
            "id",
            "full_name",
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "phone",
            "address",
            "website",
            "linkedin",
            "github",
            "nationality",
            "date_of_birth",
            "profile_summary",
            "career_objective",
            "educations",
            "certificates",
            "work_experiences",
            "projects",
            "technical_skills",
            "soft_skills",
            "achievements",
            "languages",
            "references",
        ]

    # --- Basic user info ---
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.middle_name or ''} {obj.last_name}".strip()

    def get_profile_summary(self, obj):
        personal = PersonalDetail.objects.filter(user=obj).first()
        return personal.profile_summary if personal else None

    def get_career_objective(self, obj):
        objective = CareerObjective.objects.filter(user=obj).first()
        return objective.career_objective if objective else None

    # --- Related Models ---
    def get_educations(self, obj):
        return [
            {
                "degree": e.degree,
                "institution": e.institution,
                "start_date": e.start_date,
                "end_date": e.end_date,
                "grade": e.grade,
                "location": e.location,
            }
            for e in Education.objects.filter(user=obj)
        ]

    def get_certificates(self, obj):
        return [
            {
                "name": c.name,
                "issuer": c.issuer,
                "date": c.date,
            }
            for c in Certificate.objects.filter(profile__user=obj)
        ]

    def get_work_experiences(self, obj):
        work_list = []
        for work in WorkExperience.objects.filter(user=obj):
            responsibilities = [
                r.description for r in Responsibility.objects.filter(work_experience=work)
            ]
            work_list.append({
                "company": work.company,
                "location": work.location,
                "job_title": work.job_title,
                "start_date": work.start_date,
                "end_date": work.end_date,
                "responsibilities": responsibilities,
            })
        return work_list

    def get_projects(self, obj):
        project_list = []
        for project in Project.objects.filter(user=obj):
            techs = [t.name for t in Technology.objects.filter(project=project)]
            project_list.append({
                "title": project.title,
                "description": project.description,
                "link": project.link,
                "technologies": techs,
            })
        return project_list

    def get_technical_skills(self, obj):
        return [
            t.skill_name for t in TechnicalSkill.objects.filter(skillset__user=obj)
        ]

    def get_soft_skills(self, obj):
        return [
            s.skill_name for s in SoftSkill.objects.filter(skillset__user=obj)
        ]

    def get_achievements(self, obj):
        achievements = Achievement.objects.filter(achievement_profile__user=obj)
        return [a.title for a in achievements]

    def get_languages(self, obj):
        return [
            {"language": l.language, "proficiency": l.proficiency}
            for l in Language.objects.filter(user=obj)
        ]

    def get_references(self, obj):
        return [
            {
                "name": r.name,
                "position": r.position,
                "email": r.email,
                "phone": r.phone,
            }
            for r in Reference.objects.filter(user=obj)
        ]

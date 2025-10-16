from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from api.serializers import UserDetailSerializer
from api.models import UserTB
from cv_app.services.cv_tradition_generator.core import generate_cv as generate_cv_basic
from cv_app.services.cv_intermideate_generator.cv_generator import generate_cv as generate_cv_intermediate
from cv_app.services.cv_advanced_generator.cv_generator import generate_cv_safe as generate_cv_advanced
import io

class UserCVDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get_user_cv_data(self, user: UserTB) -> dict:
        """Convert authenticated user object into detailed CV JSON."""
        serializer = UserDetailSerializer(user)
        data = serializer.data

        def title_case(s: str):
            return " ".join([w.capitalize() for w in s.split()]) if s else ""

        # ----- BASIC PERSONAL DETAILS -----
        personal = data.get("personal_details", {}) or {}
        full_name = title_case(" ".join(filter(None, [
            data.get("first_name"),
            data.get("middle_name"),
            data.get("last_name")
        ])))

        # Format phone
        phone = personal.get("phone", "")
        if phone and not phone.startswith("+"):
            phone = f"+{phone}"

        # Career Objective
        career_objective_list = data.get("career_objectives", [])
        career_objective = career_objective_list[0].get("career_objective", "") if career_objective_list else ""

        # ----- EDUCATIONS -----
        educations = [
            {
                "degree": e.get("degree", ""),
                "institution": title_case(e.get("institution", "")),
                "start_date": e.get("start_date", ""),
                "end_date": e.get("end_date", ""),
                "grade": e.get("grade", ""),
                "location": e.get("location", "")
            }
            for e in data.get("educations", [])
        ]

        # ----- CERTIFICATES -----
        profile = data.get("profile", {}) or {}
        certificates = [
            {
                "name": c.get("name", ""),
                "issuer": c.get("issuer", ""),
                "date": c.get("date", "")
            }
            for c in profile.get("certificates", [])
        ]

        # ----- WORK EXPERIENCES -----
        work_experiences = []
        for we in data.get("work_experiences", []):
            responsibilities = [
                r.get("value", "") if isinstance(r, dict) else str(r)
                for r in we.get("responsibilities", [])
            ]
            work_experiences.append({
                "company": title_case(we.get("company", "")),
                "location": we.get("location", ""),
                "job_title": title_case(we.get("job_title", "")),
                "start_date": we.get("start_date", ""),
                "end_date": we.get("end_date", ""),
                "responsibilities": [r.rstrip(".") + "." for r in responsibilities if r]
            })

        # ----- PROJECTS -----
        projects = []
        for p in data.get("projects", []):
            techs = [
                t.get("value", "") if isinstance(t, dict) else str(t)
                for t in p.get("technologies", [])
            ]
            projects.append({
                "title": title_case(p.get("title", "")),
                "description": p.get("description", ""),
                "link": p.get("link", ""),
                "technologies": [t for t in techs if t]
            })

        # ----- SKILLS -----
        skill_set = data.get("skill_sets", [{}])[0] if data.get("skill_sets") else {}
        technical_skills = [t.get("value") for t in skill_set.get("technical_skills", []) if t.get("value")]
        soft_skills = [s.get("value") for s in skill_set.get("soft_skills", []) if s.get("value")]

        # ----- ACHIEVEMENTS -----
        achievements = [
            (a.get("value") if isinstance(a, dict) else str(a)).rstrip(".") + "."
            for a in (data.get("achievement_profile", {}) or {}).get("achievements", [])
        ]

        # ----- LANGUAGES -----
        languages = [
            {"language": l.get("language", ""), "proficiency": l.get("proficiency", "")}
            for l in data.get("languages", [])
        ]

        # ----- REFERENCES -----
        references = [
            {
                "name": r.get("name", ""),
                "position": r.get("position", ""),
                "email": r.get("email", ""),
                "phone": r.get("phone", "")
            }
            for r in data.get("references", [])
        ]

        # ✅ FINAL STRUCTURE
        return {
            "id": data.get("id"),
            "full_name": full_name,
            "first_name": title_case(data.get("first_name", "")),
            "middle_name": title_case(data.get("middle_name", "")),
            "last_name": title_case(data.get("last_name", "")),
            "email": data.get("email", ""),
            "phone": phone,
            "address": personal.get("address", ""),
            "website": personal.get("website", ""),
            "linkedin": personal.get("linkedin", ""),
            "profile_image": personal.get("profile_image") , # path relative to MEDIA_ROOT
            "github": personal.get("github", ""),
            "nationality": personal.get("nationality", ""),
            "date_of_birth": personal.get("date_of_birth", ""),
            "profile_summary": personal.get("profile_summary", ""),
            "career_objective": career_objective,
            "educations": educations,
            "certificates": certificates,
            "work_experiences": work_experiences,
            "projects": projects,
            "technical_skills": technical_skills,
            "soft_skills": soft_skills,
            "achievements": achievements,
            "languages": languages,
            "references": references
        }

    def get(self, request, cv_type="basic"):
        """Return JSON or generate PDF CV."""
        try:
            user = request.user
            user_data = self.get_user_cv_data(user)

            # --- If JSON view requested ---
            if request.query_params.get("format") == "json":
                return Response(user_data, status=status.HTTP_200_OK)

            # --- Otherwise, generate PDF ---
            buffer = io.BytesIO()
            if cv_type.lower() == "basic":
                generate_cv_basic(user_data, buffer)
            elif cv_type.lower() == "intermediate":
                generate_cv_intermediate(user_data, output_path=buffer)
            elif cv_type.lower() == "advanced":
                generate_cv_advanced(user_data, output_path=buffer)
            else:
                return Response({"detail": "Invalid CV type."}, status=status.HTTP_400_BAD_REQUEST)

            buffer.seek(0)
            response = HttpResponse(buffer, content_type="application/pdf")
            response["Content-Disposition"] = f'attachment; filename="{user.first_name}_{user.last_name}_CV.pdf"'
            return response

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
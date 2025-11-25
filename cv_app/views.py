from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from api.serializers import UserDetailSerializer
from .serializers import AIGenerateSerializer
from django.conf import settings
import requests
import json
from rest_framework import status, permissions
from api.models import UserTB
from cv_app.services.cv_tradition_generator.core import generate_cv as generate_cv_basic
from cv_app.services.cv_intermideate_generator.cv_generator import generate_cv as generate_cv_intermediate
from cv_app.services.cv_advanced_generator.cv_generator import generate_cv_safe as generate_cv_advanced
import logging
logger = logging.getLogger(__name__)  
import io,os
OPENROUTER_URL = getattr(
    settings,
    "OPENROUTER_URL",
    "https://openrouter.ai/api/v1/chat/completions"
)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

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

# Build full_name from personal_details
        full_name = title_case(" ".join(filter(None, [
            personal.get("first_name", ""),
            personal.get("middle_name", ""),
            personal.get("last_name", "")
        ])))

        # Fallback to top-level fields if personal_details is missing
        if not full_name.strip():
            full_name = title_case(" ".join(filter(None, [
                data.get("first_name", ""),
                data.get("middle_name", ""),
                data.get("last_name", "")
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
            "first_name": title_case(personal.get("first_name", "")),
            "middle_name": title_case(personal.get("middle_name", "")),
            "last_name": title_case(personal.get("last_name", "")),
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
        

SECTION_FORMATS = {
    "personal_information": {
    "array_field": "personal_information",
        "template": {
            "first_name": "",
            "middle_name": "",
            "last_name": "",
            "phone": "",
            "address": "",
            "linkedin": "",
            "github": "",
            "website": "",
            "date_of_birth": "",
            "nationality": "",
            "profile_summary": ""
        }
    },

    "work_experience": {
        "array_field": "experiences",
        "template": {
            "job_title": "",
            "company": "",
            "location": "",
            "start_date": "",
            "end_date": "",
            "responsibilities": [{"value": ""}],
        }
    },
    "education": {
        "array_field": "educations",
        "template": {
            "degree": "",
            "institution": "",
            "location": "",
            "start_date": "",
            "end_date": "",
            "grade": ""
        }
    },
    "skills": {
        "array_field": "skills",
        "template": {
            "technicalSkills": [{"value": ""}],
            "softSkills": [{"value": ""}]
        }
    },
    "languages": {
        "array_field": "languages",
        "template": {
            "language": "",
            "proficiency": ""
        }
    },
    "certifications": {
        "array_field": "certificates",
        "template": {
            "name": "",
            "issuer": "",
            "date": ""
        }
    },
    "projects": {
        "array_field": "projects",
        "template": {
            "title": "",
            "description": "",
            "link": "",
            "technologies": [{"value": ""}]
        }
    },
    "achievements": {
        "array_field": "achievements",
        "template": {"value": ""}
    },
    "references": {
        "array_field": "references",
        "template": {
            "name": "",
            "position": "",
            "email": "",
            "phone": ""
        }
    },
    # Add more sections as needed
}
class CVAIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logger.info("CVAIView POST called with data: %s", request.data)

        serializer = AIGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        section = serializer.validated_data.get("section")
        user_data = serializer.validated_data.get("userData", {})
        ai_input_text = user_data.get("instruction_text") or user_data.get("prompt")

        if not ai_input_text:
            error_msg = "instruction_text or prompt is required in userData"
            logger.error(error_msg)
            return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)

        # Determine AI output format based on section
        section_format = SECTION_FORMATS.get(section, {"array_field": "items", "template": {}})

        prompt = f"""
        You are an expert CV data extractor.
        Extract all relevant information for the CV section '{section}' from the text below.
        Return a valid JSON object only.
        If multiple items exist, put them inside the array '{section_format['array_field']}'.
        Use this template for each item: {json.dumps(section_format['template'])}
        If any field is missing, set it to an empty string "".

        Text:
        \"\"\"{ai_input_text}\"\"\"
        """

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Referer": settings.FRONTEND_BASE_URL,
            "X-Title": "Gendocs CV Generator",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0
        }

        logger.info("Sending request to OpenRouter: %s", payload)

        try:
            response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            logger.info("Received AI response: %s", data)

            choice = data.get("choices", [{}])[0]
            ai_text = (
                choice.get("message", {}).get("content")
                or choice.get("text")
                or ""
            ).strip()

            if not ai_text:
                logger.error("AI returned EMPTY content: %s", data)
                return Response({"error": "AI returned empty response", "raw": data},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Remove markdown fences
            clean_text = ai_text.replace("```json", "").replace("```", "").strip()
            logger.info("Cleaned AI JSON Text: %s", clean_text)

            # Parse JSON
            try:
                ai_json = json.loads(clean_text)

                # Ensure array structure
                array_field = section_format['array_field']
                template = section_format['template']

                if array_field not in ai_json or not isinstance(ai_json[array_field], list):
                    # If AI returned a single object, wrap it in array
                    if isinstance(ai_json, dict):
                        ai_json = {array_field: [ai_json]}
                    else:
                        return Response(
                            {"error": "AI response format invalid", "raw_ai_output": ai_text},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                        )

                # Ensure each item has all keys from template
                for item in ai_json[array_field]:
                    if isinstance(template, dict):
                        for k, v in template.items():
                            if k not in item:
                                item[k] = v
                    elif isinstance(template, list) and template and isinstance(template[0], dict):
                        # for nested arrays like responsibilities
                        for k in template[0]:
                            if k not in item:
                                item[k] = [{k: ""}]

            except json.JSONDecodeError:
                logger.exception("Failed to parse AI JSON.")
                return Response(
                    {"error": "Failed to parse AI response as JSON",
                     "raw_ai_output": ai_text,
                     "cleaned_output": clean_text},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return Response(ai_json, status=status.HTTP_200_OK)

        except requests.RequestException as e:
            logger.exception("Request to OpenRouter failed.")
            return Response({"error": "Request to OpenRouter failed", "detail": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception("Unexpected error in CVAIView.")
            return Response({"error": "Unexpected server error", "detail": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
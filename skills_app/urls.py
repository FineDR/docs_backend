from django.urls import path
from .views import SkillSetView, SkillSetDetailView,SoftSkillDetailView,TechnicalSkillDetailView

urlpatterns = [
    path("skills/", SkillSetView.as_view(), name="skills"),
    path("skills/<int:pk>/", SkillSetDetailView.as_view(), name="skill-detail"),
    path("skills/technical/<int:pk>/", TechnicalSkillDetailView.as_view(), name="technical-skill-detail"),
    path("skills/soft/<int:pk>/", SoftSkillDetailView.as_view(), name="soft-skill-detail"),
]

from django.urls import path
from .views import SkillSetView, SkillSetDetailView

urlpatterns = [
    path("skills/", SkillSetView.as_view(), name="skills"),
    path("skills/<int:pk>/", SkillSetDetailView.as_view(), name="skill-detail"),
]

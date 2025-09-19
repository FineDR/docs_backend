from django.urls import path
from .views import EducationView, EducationDetailView

urlpatterns = [
    path("education/", EducationView.as_view(), name="education"),
    path("education/<int:pk>/", EducationDetailView.as_view(), name="education-detail"),
]

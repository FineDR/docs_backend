from django.urls import path
from .views import WorkExperienceView

urlpatterns = [
    path("work-experiences/", WorkExperienceView.as_view(), name="work-experiences-list"),
    path("work-experiences/<int:pk>/", WorkExperienceView.as_view(), name="work-experiences-detail"),
]

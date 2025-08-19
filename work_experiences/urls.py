from django.urls import path
from .views import WorkExperienceView

urlpatterns = [
    # Single endpoint, supports GET (list), POST (create), PUT & DELETE require pk
    path("work-experiences/", WorkExperienceView.as_view(), name="work-experiences-list"),
    path("work-experiences/<int:pk>/", WorkExperienceView.as_view(), name="work-experiences-detail"),
]

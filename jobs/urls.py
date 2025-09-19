from django.urls import path
from .views import JobPostListAPIView

urlpatterns = [
    path("jobs/", JobPostListAPIView.as_view(), name="api-job-list"),
]

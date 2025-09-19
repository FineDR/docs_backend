from django.urls import path
from .views import ProjectView, ProjectDetailView

urlpatterns = [
    path("projects/", ProjectView.as_view(), name="projects"),
    path("projects/<int:pk>/", ProjectDetailView.as_view(), name="project-detail"),
]

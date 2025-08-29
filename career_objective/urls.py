from django.urls import path
from .views import CareerObjectiveView

urlpatterns = [
    # List or create
    path("career-objective/", CareerObjectiveView.as_view(), name="career-objective-list"),
    # Detail/update/delete by ID
    path("career-objective/<int:pk>/", CareerObjectiveView.as_view(), name="career-objective-detail"),
]

from django.urls import path
from .views import CareerObjectiveView

urlpatterns = [
    path("career-objective/", CareerObjectiveView.as_view(), name="career-objective"),
]

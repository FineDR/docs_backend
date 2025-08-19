from django.urls import path
from .views import AchievementProfileView

urlpatterns = [
    path("achievements/", AchievementProfileView.as_view(), name="achievements"),
]

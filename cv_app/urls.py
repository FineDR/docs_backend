from django.urls import path
from .views import UserCVDetailsView

urlpatterns = [
    path('cv/download/<str:cv_type>/', UserCVDetailsView.as_view(), name='user-cv-download'),
]

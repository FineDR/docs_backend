from django.urls import path
from .views import PersonalDetailView

urlpatterns = [
    # Handles GET, POST, PUT, DELETE all at /api/personal-details/
    path('personal-details/', PersonalDetailView.as_view(), name='personal-details'),
]

from django.urls import path
from .views import ProfileView

urlpatterns = [
    path("certificates/", ProfileView.as_view(), name="certificates"),  
]

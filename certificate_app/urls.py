from django.urls import path
from .views import ProfileView, CertificateDetailView

urlpatterns = [
    path("certificates/", ProfileView.as_view(), name="certificates"),  
    path("certificates/<int:id>/", CertificateDetailView.as_view(), name="certificate-detail"),
]

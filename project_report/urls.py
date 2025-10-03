from django.urls import path
from .views import generate_project_pdf

urlpatterns = [
    path('report/generate-pdf/', generate_project_pdf, name='generate_pdf'),
]

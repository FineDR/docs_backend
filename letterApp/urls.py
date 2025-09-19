from django.urls import path
from .views import GenerateLetterAPIView, LetterListCreateAPIView, LetterDetailAPIView

urlpatterns = [
    path("generate-letter/", GenerateLetterAPIView.as_view(), name="generate-letter"),
    path("letters/", LetterListCreateAPIView.as_view(), name="letter-list"),
    path("letters/<int:pk>/", LetterDetailAPIView.as_view(), name="letter-detail"),
]

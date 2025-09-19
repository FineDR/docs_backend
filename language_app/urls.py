from django.urls import path
from .views import LanguageView, LanguageDetailView

urlpatterns = [
    # List all languages or create new entries
    path("languages/", LanguageView.as_view(), name="languages-list-create"),

    # Retrieve, update, or delete a specific language entry
    path("languages/<int:pk>/", LanguageDetailView.as_view(), name="language-detail"),
]

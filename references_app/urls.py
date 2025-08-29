from django.urls import path
from .views import ReferenceView

urlpatterns = [
    path("references/", ReferenceView.as_view(), name="references"),
    path("references/<int:pk>/", ReferenceView.as_view(), name="reference-detail"),
]

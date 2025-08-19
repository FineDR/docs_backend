from django.urls import path
from .views import ReferenceView

urlpatterns = [
    path("references/", ReferenceView.as_view(), name="references"),
]

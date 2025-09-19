from django.db import models
from django.conf import settings

class Language(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="languages")
    language = models.CharField(max_length=100)
    proficiency = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.language} ({self.proficiency})"

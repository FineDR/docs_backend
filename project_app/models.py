from django.db import models
from django.conf import settings

class Project(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=255)
    description = models.TextField()
    link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Technology(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="technologies")
    value = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.value} ({self.project.title})"

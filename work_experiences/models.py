from django.db import models
from django.conf import settings

class WorkExperience(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="work_experiences"
    )
    job_title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.job_title} at {self.company} ({self.user.email})"


class Responsibility(models.Model):
    work_experience = models.ForeignKey(
        WorkExperience,
        on_delete=models.CASCADE,
        related_name="responsibilities"
    )
    value = models.CharField(max_length=500)

    def __str__(self):
        return self.value

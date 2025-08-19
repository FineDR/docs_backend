from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Education(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="educations")
    degree = models.CharField(max_length=255)
    institution = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    grade = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.degree} - {self.institution}"

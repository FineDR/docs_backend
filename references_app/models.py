from django.db import models
from django.conf import settings

class Reference(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='references'
    )
    name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name} ({self.position}) - {self.user.email}"

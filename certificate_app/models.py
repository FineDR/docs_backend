from django.db import models
from django.conf import settings

class Profile(models.Model):
    """
    Stores personal details for a single user.
    One-to-one relationship with the user model.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    full_name = models.CharField(max_length=255)
    email = models.EmailField()

    def __str__(self):
        return f"{self.full_name} Profile"


class Certificate(models.Model):
    """
    Stores certificate information linked to a Profile.
    One profile can have multiple certificates.
    """
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="certificates"
    )
    name = models.CharField(max_length=255)
    issuer = models.CharField(max_length=255)
    date = models.DateField()

    def __str__(self):
        return f"{self.name} ({self.issuer})"

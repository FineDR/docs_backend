from django.db import models
from django.conf import settings

class AchievementProfile(models.Model):
    """
    Stores achievements for a single user.
    One-to-one relationship with the user model.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="achievement_profile"
    )
    full_name = models.CharField(max_length=255)
    email = models.EmailField()

    def __str__(self):
        return f"{self.full_name} Achievements"


class Achievement(models.Model):
    """
    Stores individual achievements linked to an AchievementProfile.
    One profile can have multiple achievements.
    """
    profile = models.ForeignKey(
        AchievementProfile,
        on_delete=models.CASCADE,
        related_name="achievements"
    )
    value = models.TextField()

    def __str__(self):
        return f"{self.value[:50]}..."  # first 50 chars

    @property
    def id(self):
        return self.pk  # Django automatically provides pk; this makes id explicit for frontend

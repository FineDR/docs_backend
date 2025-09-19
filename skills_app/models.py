from django.db import models
from django.conf import settings

class SkillSet(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="skill_sets"
    )
    full_name = models.CharField(max_length=255)
    email = models.EmailField()

    def __str__(self):
        return f"Skills for {self.full_name}"


class TechnicalSkill(models.Model):
    skill_set = models.ForeignKey(
        SkillSet,
        on_delete=models.CASCADE,
        related_name="technical_skills"
    )
    value = models.CharField(max_length=255)

    def __str__(self):
        return self.value


class SoftSkill(models.Model):
    skill_set = models.ForeignKey(
        SkillSet,
        on_delete=models.CASCADE,
        related_name="soft_skills"
    )
    value = models.CharField(max_length=255)

    def __str__(self):
        return self.value

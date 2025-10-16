from django.db import models
from django.conf import settings

class PersonalDetail(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='personal_detail'
    )
    phone = models.CharField(max_length=20)
    address = models.TextField()
    linkedin = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    date_of_birth = models.DateField()
    nationality = models.CharField(max_length=100)
    profile_summary = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(
        upload_to='profile_images/',  # folder where images will be stored
        blank=True,
        null=True
    )

    def __str__(self):
        full_name = " ".join(filter(None, [self.user.first_name, self.user.middle_name, self.user.last_name]))
        return f"{full_name} Personal Detail"

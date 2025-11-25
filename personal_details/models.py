from django.db import models
from django.conf import settings

class PersonalDetail(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='personal_detail'
    )

    # Added name fields
    first_name = models.CharField(max_length=150 ,default='')
    middle_name = models.CharField(max_length=150, blank=True, null=True, default='')
    last_name = models.CharField(max_length=150, default='')

    phone = models.CharField(max_length=20)
    address = models.TextField()

    # Changed URLFields to CharFields to store plain strings
    linkedin = models.CharField(max_length=255, blank=True, null=True)
    github = models.CharField(max_length=255, blank=True, null=True)
    website = models.CharField(max_length=255, blank=True, null=True)

    date_of_birth = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    profile_summary = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(
        upload_to='profile_images/',  # folder where images will be stored
        blank=True,
        null=True
    )

    def __str__(self):
        full_name = " ".join(filter(None, [self.first_name, self.middle_name, self.last_name]))
        return f"{full_name} Personal Detail"

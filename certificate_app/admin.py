from django.contrib import admin
from .models import Profile, Certificate

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "user")
    search_fields = ("full_name", "email", "user__email")

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("name", "issuer", "date", "profile")
    search_fields = ("name", "issuer", "profile__full_name", "profile__email")

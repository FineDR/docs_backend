from django.contrib import admin
from .models import PersonalDetail

@admin.register(PersonalDetail)
class PersonalDetailAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "address", "linkedin", "github", "website")
    search_fields = ("user__email", "user__full_name", "phone", "nationality")

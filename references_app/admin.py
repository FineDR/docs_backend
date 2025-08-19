from django.contrib import admin
from .models import Reference

@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    list_display = ("name", "position", "email", "phone", "user")
    search_fields = ("name", "position", "email", "user__email")

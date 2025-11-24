# admin.py
from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "external_id",
        "transaction_id",
        "account_number",
        "provider",
        "amount",
        "status",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "provider", "created_at")
    search_fields = ("external_id", "transaction_id", "account_number")

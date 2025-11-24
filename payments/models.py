from django.db import models



class Transaction(models.Model):
    external_id = models.CharField(max_length=100, unique=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)  # Added
    account_number = models.CharField(max_length=20, blank=True, null=True)
    provider = models.CharField(max_length=50, blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=50, default="PENDING")  
    raw_checkout = models.JSONField(blank=True, null=True)  # Added
    raw_callback = models.JSONField(blank=True, null=True)
    raw_webhook = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.external_id} - {self.status}"


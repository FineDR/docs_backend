# payments/models.py
from django.db import models

class Transaction(models.Model):
    external_id = models.CharField(max_length=100, unique=True)
    provider = models.CharField(max_length=50)
    account_number = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.external_id} - {self.status}"

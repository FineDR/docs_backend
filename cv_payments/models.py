import uuid
from django.db import models
from django.conf import settings

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]
    PROVIDER_CHOICES = [
        ('selcom', 'Selcom'),
        ('flutterwave', 'Flutterwave'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cv_id = models.CharField(max_length=100)
    amount = models.PositiveIntegerField(default=3000)
    currency = models.CharField(max_length=10, default='TZS')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, blank=True, null=True)
    provider_ref = models.CharField(max_length=100, blank=True, null=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.cv_id} - {self.status}"

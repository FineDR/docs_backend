from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Letter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="letters")
    recipient = models.CharField(max_length=255)
    recipient_title = models.CharField(max_length=255)
    recipient_address = models.TextField()
    purpose = models.TextField()
    sender_name = models.CharField(max_length=255)
    sender_phone = models.CharField(max_length=50)

    # AI cleaned fields
    subject = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)
    closing = models.CharField(max_length=255, default="Sincerely,")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Letter to {self.recipient} by {self.sender_name}"

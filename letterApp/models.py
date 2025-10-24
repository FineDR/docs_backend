from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Letter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="letters")
    recipient = models.CharField(max_length=255)
    recipient_title = models.CharField(max_length=255)
    recipient_address = models.TextField()
    sender = models.CharField(max_length=255)
    sender_title = models.CharField(max_length=255, blank=True)
    sender_address = models.CharField(max_length=255, blank=True)
    date = models.DateField(blank=True, null=True)
    
    # AI cleaned fields
    subject = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)
    closing = models.CharField(max_length=255, default="Sincerely,")
    sender_signature = models.TextField(blank=True, null=True)
    lang = models.CharField(max_length=2, choices=[("en","English"),("sw","Swahili")], default="en")
    align_contact = models.CharField(max_length=5, choices=[("start","start"),("end","end")], default="start")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Letter to {self.recipient} by {self.sender}"

# api/utils.py
from django.core.mail import send_mail
from threading import Thread

def send_mail_async(subject, message, from_email, recipient_list):
    Thread(target=send_mail, args=(subject, message, from_email, recipient_list), kwargs={'fail_silently': False}).start()

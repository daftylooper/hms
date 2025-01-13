from celery import shared_task
from .models import *
from .emailer import send_email

@shared_task(serializer='pickle')
def send_email_task(subject, body, to_email):
    send_email(subject, body, to_email)
    return {"success": "success"}
from .models import *
from .serializer import *
from rest_framework.response import Response
from rest_framework import status
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from utils.logger import log, Level
from utils.models import Log
from dotenv import load_dotenv
import os

load_dotenv()
alog = Log()

@receiver(post_save, sender=Patient)
def doctor_post_save(sender, instance, created, *args, **kwargs):
    if created:
        log(Level.INFO, "Save Action Recorded into Action Log!")
        alog.log_action(f"POST REQUEST: Saved Doctor Instance - {instance.id}")
    # else:
    #     log(Level.ERROR, "Object Couldn't Be Saved to Table!")
    #     alog.log_action("POST REQUEST: Couldn't Save Doctor Instance")

@receiver(post_delete, sender=Patient)
def doctor_post_delete(sender, instance, using, *args, **kwargs):
    log(Level.INFO, "Delete Action Recorded into Action Log!")
    alog.log_action(f"DELETE REQUEST: Delete Doctor Instance - {instance.id}")
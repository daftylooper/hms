from .models import *
from .serializer import *
from rest_framework.response import Response
from rest_framework import status
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from utils.logger import log, Level
from utils.models import Log
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.hashers import make_password
from dotenv import load_dotenv
import os

load_dotenv()
alog = Log()

# @receiver(post_save, sender=Patient)
# def patient_post_save(sender, instance, created, *args, **kwargs):
#     if created:
#         log(Level.INFO, "Save Action Recorded into Action Log!")
#         alog.log_action(f"POST REQUEST: Saved Patient Instance - {instance.id}")
#     # else:
#     #     log(Level.ERROR, "Object Couldn't Be Saved to Table!")
#     #     alog.log_action("POST REQUEST: Couldn't Save Doctor Instance")

# @receiver(post_delete, sender=Patient)
# def patient_post_delete(sender, instance, using, *args, **kwargs):
#     log(Level.INFO, "Delete Action Recorded into Action Log!")
#     alog.log_action(f"DELETE REQUEST: Delete Patient Instance - {instance.id}")

@receiver(post_save, sender=Patient)
def create_user_post_save(sender, instance, created, *args, **kwargs):
    if created:
        log(Level.INFO, "Creating User for New Patient")
        user = User.objects.create(
            username=instance.name,
            email=instance.email,
            password=make_password('default') # user is created by hospital staff, user should be allowed to change password later
        )

        group = Group.objects.get(name="PatientUser")
        user.groups.add(group)
        user.save()

        print("fool of a took", user.id)
        instance.populate_userid(user)

@receiver(post_delete, sender=Patient)
def delete_user_post_delete(sender, instance, using, *args, **kwargs):
    deleted_count, _ = User.objects.filter(email=instance.email).delete()
    if deleted_count > 0:
        log(Level.INFO, f"User {instance.name} with email deleted successfully.")
    else:
        log(Level.WARNING, f"No user found with email '{instance.email}'.")
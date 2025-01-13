from .models import *
from .serializer import *
from django.dispatch import receiver
from django.db.models.signals import *
from utils.logger import log, Level

@receiver(post_save, sender=Doctor)
def doctor_post_save(sender, instance, created, *args, **kwargs):
    if created:
        log(Level.INFO, "Doctor Object Created!")
    print(args, kwargs)
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from utils.logger import log, Level
from utils.models import Log
from django.apps import apps
import json

alog = Log()

def model_to_json(instance):
    serialized = {}
    for key, value in instance.__dict__.items():
        try:
            json.dumps(value)
            serialized[key] = value
        except Exception:
            continue
    return serialized

def log_model_save(sender, instance, created, **kwargs):
    if created:
        log(Level.INFO, f"Save Action Recorded into Action Log for {sender.__name__}!")
        alog.log_action(f"POST REQUEST: Saved {sender.__name__} Instance - {instance.id}")

def log_model_delete(sender, instance, **kwargs):
    log(Level.INFO, f"Delete Action Recorded into Action Log for {sender.__name__}!")
    alog.log_action(f"DELETE REQUEST: Deleted {sender.__name__} Instance - {instance.id} - {json.dumps(model_to_json(instance))}")

# tracking all models, attach a signal
excluded = [Log] # dont log the log because recursion
for model in apps.get_models():
    if model not in excluded:
        post_save.connect(log_model_save, sender=model)
        post_delete.connect(log_model_delete, sender=model)
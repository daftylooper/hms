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

from django.core.handlers.wsgi import WSGIRequest
import threading
import json

def log_model_save(sender, instance, created, **kwargs):
    try:
        # store request stuff in thread local storage( for the log )
        request = getattr(threading.current_thread(), '_current_request', None)
        metadata = {
            'model': sender.__name__,
            'instance_id': instance.id,
            'instance_data': str(instance)  # or a more detailed serialization if needed
        }
        method = 'POST' if created else 'PUT/PATCH'
        action_type = 'Created' if created else 'Updated'
        
        # make log entry
        alog.log_action(
            action=f"{method} REQUEST: {action_type} {sender.__name__} Instance - {instance.id}",
            actor=getattr(request, 'jwt_user', None) if request else None,
            ip_address=getattr(request, 'client_ip', None) if request else None,
            method=method,
            metadata=metadata
        )
        
        log(Level.INFO, f"{action_type} Action Recorded into Action Log for {sender.__name__}!")
    except AttributeError:
        pass
    except Exception as e:
        log(Level.ERROR, f"Error in log_model_save: {e}")

# def log_model_delete(sender, instance, **kwargs):
#     try:
#         log(Level.INFO, f"Delete Action Recorded into Action Log for {sender.__name__}!")
#         alog.log_action(f"DELETE REQUEST: Deleted {sender.__name__} Instance - {instance.id} - {json.dumps(model_to_json(instance))}")
#     except AttributeError:
#         pass
#     except Exception as e:
#         log(Level.ERROR, f"Error in log_model_delete: {e}")

def log_model_delete(sender, instance, **kwargs):
    try:
        request = getattr(threading.current_thread(), '_current_request', None)
        
        metadata = {
            'model': sender.__name__,
            'instance_id': instance.id,
            'instance_data': str(instance)
        }
        
        alog.log_action(
            action=f"DELETE REQUEST: Deleted {sender.__name__} Instance - {instance.id}",
            actor=getattr(request, 'jwt_user', None) if request else None,
            ip_address=getattr(request, 'client_ip', None) if request else None,
            method='DELETE',
            metadata=metadata
        )
        
        log(Level.INFO, f"Delete Action Recorded into Action Log for {sender.__name__}!")
    except AttributeError:
        pass
    except Exception as e:
        log(Level.ERROR, f"Error in log_model_delete: {e}")

# tracking all models, attach a signal
excluded = [Log] # dont log the log because recursion
for model in apps.get_models():
    if model not in excluded:
        post_save.connect(log_model_save, sender=model)
        post_delete.connect(log_model_delete, sender=model)
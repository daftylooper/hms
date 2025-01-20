# from django.db import models

# class Log(models.Model):
#     timestamp = models.DateTimeField(auto_now_add=True)
#     action = models.TextField(max_length=1024)


#     @classmethod
#     def log_action(cls, action):
#         # note: don't log the log creation, will put it in endless recursion
#         return cls.objects.create(
#             action=action
#         )

from django.conf import settings
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User

class Log(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='audit_logs'
    )
    
    # IP Address of the request
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # The actual action description
    action = models.TextField(max_length=1024)
    
    # Target object information using GenericForeignKey
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.CharField(max_length=255, null=True)
    target = GenericForeignKey('content_type', 'object_id')
    
    # Request method (POST, PUT, PATCH, DELETE)
    method = models.CharField(max_length=10, null=True)
    
    # Additional metadata stored as JSON
    metadata = models.JSONField(default=dict, blank=True)

    @classmethod
    def log_action(cls, action, actor=None, ip_address=None, target=None, method=None, metadata=None):
        # note: don't log the log creation, will put it in endless recursion
        return cls.objects.create(
            action=action,
            actor=actor,
            ip_address=ip_address,
            content_type=ContentType.objects.get_for_model(target) if target else None,
            object_id=str(target.pk) if target else None,
            method=method,
            metadata=metadata or {}
        )
from django.conf import settings
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User

class Log(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    actor = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='audit_logs'
    )
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    # The actual action description
    action = models.TextField(max_length=1024)
    method = models.CharField(max_length=10, null=True)    
    metadata = models.JSONField(default=dict, blank=True)

    @classmethod
    def log_action(cls, action, actor=None, ip_address=None, target=None, method=None, metadata=None):
        # note: don't log the log creation, will put it in endless recursion
        return cls.objects.create(
            action=action,
            actor=actor,
            ip_address=ip_address,
            method=method,
            metadata=metadata or {}
        )
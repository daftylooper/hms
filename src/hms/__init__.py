# This will make sure the app is always imported when
# Django starts so tasks can be registered.
from .celery import app as celery_app

__all__ = ['celery_app']

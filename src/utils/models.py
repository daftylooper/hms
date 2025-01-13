from django.db import models

class Log(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.TextField(max_length=1024)

    @classmethod
    def log_action(cls, action):
        # note: don't log the log creation, will put it in endless recursion
        return cls.objects.create(
            action=action
        )
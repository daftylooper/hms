from django.db import models
from hospital.models import Hospital, Department

class Doctor(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    active = models.BooleanField(default=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

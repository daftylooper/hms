from django.db import models
from doctor.models import Doctor

# Create your models here.
class Patient(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    age = models.PositiveSmallIntegerField()
    addr = models.CharField(max_length=128)
    retired = models.BooleanField(default=False)

    def __str__(self):
        return f"patient@{self.id}@{self.name}"

class Visit(models.Model):
    class Status(models.TextChoices):
        ADMITTED = 'admitted'
        WAITING = 'waiting'
        DISCHARGED = 'discharged'

    id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.WAITING)

    patient_id = models.ForeignKey(Patient, on_delete=models.PROTECT) # a deleted patient wont affect related row in visit
    doctor_id = models.ForeignKey(Doctor, on_delete=models.PROTECT)
    # foreign key pointing to unique key in hosp-dept table??

    def __str__(self):
        return f"visit@{self.id}"
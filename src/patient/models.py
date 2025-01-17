from django.db import models
from doctor.models import Doctor
from hospital.models import *
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
class Patient(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    dob = models.DateField(default="2000-01-01")
    addr = models.CharField(max_length=128)
    phone = models.CharField(max_length=1024, null=True, blank=True)
    email = models.EmailField()
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True) # blank because it is updates post user creation

    def populate_userid(self, user_id):
        if not self.user_id: # only update if user_id blank
            self.user_id = user_id
            self.save(update_fields=['user_id'])

    # def __str__(self):
    #     return f"patient@{self.id}@{self.name}"

class Visit(models.Model):
    class Status(models.TextChoices):
        ADMITTED = 'admitted'
        WAITING = 'waiting'
        DISCHARGED = 'discharged'

    id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.WAITING)

    # a deleted patient wont affect related row in visit
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"visit@{self.id}"
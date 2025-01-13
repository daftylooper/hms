from celery import shared_task
from .models import *
from .serializer import *

@shared_task(serializer='pickle')
def create_object_task(name, hospital, department):
    doctor = Doctor.objects.create(
        name=name,
        hospital=hospital,
        department=department
    )
    return DoctorSerializer(doctor).data
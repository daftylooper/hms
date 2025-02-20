from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from datetime import datetime
from .models import *
from hospital.models import *
from doctor.models import *
from .serializer import *
from utils.tasks import send_email_task
from dotenv import load_dotenv
from functools import wraps
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
from utils.crypto import CryptUtils
from django.core.cache import cache
import json
import re
import os
import time

# tries to match user_id and caller patient_id
def check_authorisation(func):
    @wraps(func)
    def wrapper(request, pk, *args, **kwargs):
        try:
            patient = Patient.objects.get(pk=pk)
            if not request.user.is_staff and patient.user_id.id != request.user.id:
                raise PermissionDenied("You are not authorised to access this patient's information.")
        except Patient.DoesNotExist:
            raise PermissionDenied("Patient not found.")
        return func(request, pk, *args, **kwargs)

    return wrapper

class PatientList(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    @method_decorator(permission_required('patient.view_patient', raise_exception=True))
    def get(self, request):
        if not request.user.is_staff:
            return Response("You are not allowed", status=status.HTTP_403_FORBIDDEN)
        
        start_time_cache = time.time()
        cached_data = cache.get('patient_list')
        print("cached data", cached_data)
        end_time_cache = time.time()
        if cached_data is not None:
            print(f"Cache hit: {(end_time_cache - start_time_cache)*1000} ms")
            return Response(cached_data, status=status.HTTP_200_OK)

        start_time_db = time.time()
        patients = Patient.objects.all()
        serializer = PatientSerializer(patients, many=True)
        end_time_db = time.time()
        print(f"Database hit: {(end_time_db - start_time_db)*1000} ms")
        cache.set('patient_list', serializer.data, timeout=60*10)
        return Response(serializer.data)
    
    @method_decorator(permission_required('patient.change_patient', raise_exception=True))
    def post(self, request):
        load_dotenv()

        if not request.user.is_staff:
            return Response("You are not allowed", status=status.HTTP_403_FORBIDDEN)

        serializer = PatientSerializer(data=request.data)
        phone, email = request.data["phone"], request.data["email"]
        if not bool(re.fullmatch(r"((\+*)((0[ -]*)*|((91 )*))((\d{12})+|(\d{10})+))|\d{5}([- ]*)\d{6}", phone)):
            return Response("Enter a valid phone number", status=status.HTTP_400_BAD_REQUEST)
        serializer.validate_phone(phone)
        serializer.validate_email(email)
        if serializer.is_valid():
            serializer.save()
            name = request.data.get("name", "undefined")
            result = send_email_task.delay(
                "Patient Registered!",
                f"Hello, {name}!\nYou have succesfully registered as a patient. Here are your details - \n {serializer.data}",
                os.getenv("RECEIVER_MAIL")
            )
            serializer.data["task_id"] = result.id
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
            # return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PatientView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Patient.objects.get(pk=pk)
        except Patient.DoesNotExist:
            return None

    @method_decorator(permission_required('patient.view_patient', raise_exception=True))
    @method_decorator(check_authorisation)
    def get(self, request, pk):
        start_time_cache = time.time()
        cache_data = cache.get(f'patient_{pk}')
        end_time_cache = time.time()
        if cache_data is not None:
            print(f"Cache hit: {(end_time_cache - start_time_cache)*1000} ms")
            return Response(cache_data, status=status.HTTP_200_OK)
        start_time_db = time.time()
        visit = self.get_object(pk)
        if not visit:
            return Response(status.HTTP_400_BAD_REQUEST)
        serializer = PatientSerializer(visit)
        cache.set(f'patient_{pk}', serializer.data, timeout=60*10)
        end_time_db = time.time()
        print(f"Database hit: {(end_time_db - start_time_db)*1000} ms")
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @method_decorator(permission_required('patient.change_patient', raise_exception=True))
    @method_decorator(check_authorisation)
    def put(self, request, pk):
        visit = self.get_object(pk)
        if not visit:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = PatientSerializer(visit, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @method_decorator(permission_required('patient.change_patient', raise_exception=True))
    @method_decorator(check_authorisation)
    def patch(self, request, pk):
        visit = self.get_object(pk)
        if not visit:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = PatientSerializer(visit, data=request.data, partial=True)  # partial because, we doing patach requst and it updates only the fields that are provided
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @method_decorator(permission_required('patient.delete_patient', raise_exception=True))
    def delete(self, request, pk):
        visit = self.get_object(pk)
        if not visit:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        visit.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class VisitList(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser] 

    # replace all patient, hospital, department, doctor ids with actual names
    @method_decorator(permission_required('patient.view_visit', raise_exception=True))
    def get(self, request):
        visits = Visit.objects.select_related(
            'patient', 'hospital', 'department', 'doctor'
        ).all()

        visit_data = []
        for visit in visits:
            visit_data.append({
                "id": visit.id,
                "patient_name": visit.patient.name,
                "hospital_name": visit.hospital.name,
                "department_name": visit.department.name,
                "doctor_name": visit.doctor.name,
                "visit_date": visit.timestamp,
                "status": visit.status
            })

        return Response(visit_data, status=status.HTTP_200_OK)
    
    @method_decorator(permission_required('patient.change_visit', raise_exception=True))
    def post(self, request):
        serializer = VisitSerializer(data=request.data)
        if not serializer.validate(request.data):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        model_mapping = {
            "patient": Patient,
            "doctor": Doctor,
            "hospital": Hospital,
            "department": Department,
        }

        try:
            for key, model in model_mapping.items():

                obj = get_object_or_404(model, name=data.get(key))
                data[key] = obj.id

            # dont record a visit of the patient if they haven't been discharged from other places yet
            patient_id = data["patient"]
            last_visit = Visit.objects.filter(patient_id=patient_id).order_by('-timestamp').first()
            if last_visit and last_visit.status != Visit.Status.DISCHARGED:
                return Response(
                    {"error": "Patient cannot create a new visit while still admitted or waiting"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # check if the doctor is linked to the hospital and department
            hospital_id = data["hospital"]
            department_id = data["department"]
            doctor_id = data["doctor"]
            doctor = Doctor.objects.get(id=doctor_id)
            if not doctor.hospital.id==hospital_id or not doctor.department.id==department_id:
                return Response(
                    {"error": "Doctor does not belong to the specified hospital or department"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = VisitSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class VisitView(APIView):
    permission_classes = [IsAuthenticated]
    cu = CryptUtils(os.getenv('DJANGO_SECRET_KEY'))
    
    def get_age(self, date):
        today = date.today()
        year_diff = today.year - date.year
        if (today.month, today.day) < (date.month, date.day):
            year_diff -= 1
        return year_diff

    def get_object(self, pk):
        try:
            return Visit.objects.get(pk=pk)
        except Visit.DoesNotExist:
            return None

    @method_decorator(permission_required('patient.view_visit', raise_exception=True))
    @method_decorator(check_authorisation)
    def get(self, request, pk):
        try:
            patient = get_object_or_404(Patient, pk=pk)
        except Patient.DoesNotExist:
            return Response({"error": "Patient not found"}, status=status.HTTP_400_BAD_REQUEST)
        visits = Visit.objects.filter(patient=patient).order_by('-timestamp')

        if not visits.exists():
            return Response({"message": "No visits found for this patient"}, status=status.HTTP_404_NOT_FOUND)

        serializer = VisitSerializer(visits, many=True)
        return Response({
            "patient": {
                "id": patient.id,
                "name": patient.name,
                "email": patient.email,
                "address": patient.addr,
                "phone": self.cu.decrypt(patient.phone),
                "age": self.get_age(patient.dob)
            },
            "visits": serializer.data
        }, status=status.HTTP_200_OK)
    
    @method_decorator(permission_required('patient.change_visit', raise_exception=True))
    def put(self, request, pk): # too lazy to write rn
        visit = self.get_object(pk)
        if not visit:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = VisitSerializer(visit, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @method_decorator(permission_required('patient.delete_visit', raise_exception=True))
    def delete(self, request, pk):
        visit = self.get_object(pk)
        if not visit:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        visit.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class StatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Visit.objects.get(pk=pk)
        except Visit.DoesNotExist:
            return None

    @method_decorator(permission_required('patient.view_patient', raise_exception=True))
    @method_decorator(check_authorisation)
    def get(self, request, pk):
        try:
            patient = get_object_or_404(Patient, pk=pk)
        except Patient.DoesNotExist:
            return Response({"error": "Patient not found"}, status=status.HTTP_400_BAD_REQUEST)
    
        latest_visit = Visit.objects.filter(patient=patient).order_by('-timestamp').first()
        if not latest_visit:
            return Response({"message": "No visits found for this patient"}, status=status.HTTP_404_NOT_FOUND)
            
        return Response({
            "status": latest_visit.status,
            "visit_id": latest_visit.id,
            "timestamp": latest_visit.timestamp
        }, status=status.HTTP_200_OK)
    
    @method_decorator(permission_required('patient.change_patient', raise_exception=True))
    @method_decorator(check_authorisation)
    def patch(self, request, pk):
        try:
            patient = get_object_or_404(Patient, pk        # Get the latest active visit (not discharged)
=pk)
        except Patient.DoesNotExist:
            return Response({"error": "Patient not found"}, status=status.HTTP_400_BAD_REQUEST)

        visit = Visit.objects.filter(patient=patient).exclude(status=Visit.Status.DISCHARGED).order_by('-timestamp').first()
        if not visit:
            return Response({"error": "No active visits found for this patient"}, status=status.HTTP_404_NOT_FOUND)
        new_status = request.data.get("status")
        if not new_status or new_status not in Visit.Status.values:
            return Response({"error": "Invalid status value"}, status=status.HTTP_400_BAD_REQUEST)
        visit.status = new_status
        visit.save()

        return Response({
            "status": visit.status,
            "visit_id": visit.id,
            "timestamp": visit.timestamp
        }, status=status.HTTP_200_OK)
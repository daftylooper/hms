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
import json
import re
import os

class PatientList(APIView):
    def get(self, request):
        visits = Patient.objects.all()
        serializer = PatientSerializer(visits, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        load_dotenv()

        serializer = PatientSerializer(data=request.data)
        if not bool(re.fullmatch(r"((\+*)((0[ -]*)*|((91 )*))((\d{12})+|(\d{10})+))|\d{5}([- ]*)\d{6}", request.data["phone"])):
            return Response("Enter a valid phone number", status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            serializer.save()
            name = request.data.get("name", "undefined")
            result = send_email_task.delay(
                "Patient Registered!",
                f"Hello, {name}!\nYou have succesfully registered as a patient. Here are your details - \n {serializer.data}",
                os.getenv("RECEIVER_MAIL")
            )
            return Response({"task_id": result.id, "status": "Task queued"}, status=status.HTTP_202_ACCEPTED)
            # return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PatientView(APIView):
    def get_object(self, pk):
        try:
            return Patient.objects.get(pk=pk)
        except Patient.DoesNotExist:
            return None

    def get(self, request, pk):
        visit = self.get_object(pk)
        if not visit:
            return Response(status.HTTP_400_BAD_REQUEST)
        serializer = PatientSerializer(visit)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, pk):
        visit = self.get_object(pk)
        if not visit:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = PatientSerializer(visit, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        visit = self.get_object(pk)
        if not visit:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        visit.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class VisitList(APIView):
    # replace all patient, hospital, department, doctor ids with actual names
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
    
    def post(self, request):
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

            #dont record a visit of the patient if they haven't been discharged from other places yet
            patient_id = data["patient"]
            last_visit = Visit.objects.filter(patient_id=patient_id).order_by('-timestamp').first()
            if last_visit and last_visit.status != Visit.Status.DISCHARGED:
                return Response(
                    {"error": "Patient cannot create a new visit while still admitted or waiting"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            #check if the doctor is linked to the hospital and department
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

    def get(self, request, pk):
        try:
            patient = get_object_or_404(Patient, pk=pk)
        except Patient.DoesNotExist:
            return Response({"error": "Patient not found"}, status=status.HTTP_400_BAD_REQUEST)
        visits = Visit.objects.filter(patient=patient).order_by('-timestamp')

        if not visits.exists():
            return Response({"message": "No visits found for this patient"}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the visits
        serializer = VisitSerializer(visits, many=True)
        return Response({
            "patient": {
                "id": patient.id,
                "name": patient.name,
                "email": patient.email,
                "address": patient.addr,
                "phone": patient.phone,
                "age": self.get_age(patient.dob)
            },
            "visits": serializer.data
        }, status=status.HTTP_200_OK)
    
    def put(self, request, pk): # too lazy to write rn
        visit = self.get_object(pk)
        if not visit:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = VisitSerializer(visit, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        visit = self.get_object(pk)
        if not visit:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        visit.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class StatusView(APIView):
    def get_object(self, pk):
        try:
            return Visit.objects.get(pk=pk)
        except Visit.DoesNotExist:
            return None

    def get(self, request, pk):
        visit = self.get_object(pk)
        if not visit:
            return Response(status.HTTP_400_BAD_REQUEST)
        serializer = VisitSerializer(visit)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, pk):
        try:
            patient = get_object_or_404(Patient, pk=pk)
        except Patient.DoesNotExist:
            return Response({"error": "Patient not found"}, status=status.HTTP_400_BAD_REQUEST)

        visit = Visit.objects.filter(patient=patient).exclude(status=Visit.Status.DISCHARGED).order_by('-timestamp').first()
        if not visit:
            return Response({"error": "No active visits, cannot change status"}, status=status.HTTP_404_NOT_FOUND)

        serializer = VisitSerializer(visit, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
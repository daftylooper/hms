from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import *
from hospital.models import *
from doctor.models import *
from .serializer import *
import json
import re

class PatientList(APIView):
    def get(self, request):
        visits = Patient.objects.all()
        serializer = PatientSerializer(visits, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = PatientSerializer(data=request.data)
        if not bool(re.fullmatch(r"((\+*)((0[ -]*)*|((91 )*))((\d{12})+|(\d{10})+))|\d{5}([- ]*)\d{6}", request.data["phone"])):
            return Response("Enter a valid phone number", status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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
    def get_object(self, pk):
        try:
            return Visit.objects.get(pk=pk)
        except Visit.DoesNotExist:
            return None

    def get(self, request, pk):
        visit = self.get_object(pk)
        # replace all patient, hospital, department, doctor ids with actual names
        if not visit:
            return Response(status.HTTP_400_BAD_REQUEST)
        serializer = VisitSerializer(visit)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, pk): # can't think of the logic rn
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

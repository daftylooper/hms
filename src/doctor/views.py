from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.template.response import ContentNotRenderedError
from .models import *
from hospital.models import *
from .serializer import *
import json

def get_hospital_id(hospital_name):
    try:
        hospital = Hospital.objects.get(name=hospital_name)
    except Hospital.DoesNotExist:
        return Response({"error": f"Hospital '{hospital_name}' not found."}, status=status.HTTP_404_NOT_FOUND)
    return hospital

def get_department_id(department_name):
    try:
        department = Department.objects.get(name=department_name)
    except Department.DoesNotExist:
        return Response({"error": f"Department '{department_name}' not found."}, status=status.HTTP_404_NOT_FOUND)
    return department

def check_valid_pair(hospital_name, department_name):
    hospital, department = get_hospital_id(hospital_name), get_department_id(department_name)
    is_valid = HospitalDepartment.objects.filter(hospital=hospital, department=department).exists()
    return [hospital, department, is_valid]

class DoctorList(APIView):
    def get(self, request):
        doctors = Doctor.objects.all()
        serializer = DoctorSerializer(doctors, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        body = json.loads(request.body)
        try:
            name, hospital_name, department_name = body["name"], body["hospital"], body["department"]
        except KeyError as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)
        
        # retrieve hospital and department ids from name, ig they can conflict if two hospitals have same names
        hospital, department, is_valid_pair = check_valid_pair(hospital_name, department_name)
        if not is_valid_pair:
            return Response(
                {"error": f"The hospital '{hospital_name}' and department '{department_name}' are not linked."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
        print("A")
        doctor = Doctor.objects.create(
            name=name,
            hospital=hospital,
            department=department
        )
        doctor_serializer = DoctorSerializer(doctor)
        return Response(doctor_serializer.data, status=status.HTTP_201_CREATED)
        # return Response(status=status.HTTP_201_CREATED)
    
class DoctorView(APIView):
    def get_object(self, pk):
        try:
            return Doctor.objects.get(pk=pk)
        except Doctor.DoesNotExist:
            return None

    def get(self, request, pk):
        doctor = self.get_object(pk)
        if not doctor:
            return Response(status.HTTP_400_BAD_REQUEST)
        serializer = DoctorSerializer(doctor)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, pk):
        body = json.loads(request.body)
        doctor = self.get_object(pk)
        hospital, department = doctor.hospital.id, doctor.department.id

        if not doctor:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if "hospital" in body:
            hospital = get_hospital_id(body["hospital"])
        if "department" in body:
            department = get_department_id(body["department"])
        valid_pair = HospitalDepartment.objects.filter(hospital=hospital, department=department).exists()
        if not valid_pair:
            return Response(
                {"error": f"The hospital and department are not linked."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        request.data["hospital"], request.data["department"] = hospital.id, department.id
        serializer = DoctorSerializer(doctor, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        doctor = self.get_object(pk)
        if not doctor:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        doctor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.template.response import ContentNotRenderedError
from .models import *
from hospital.models import *
from .serializer import *
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
import json

def get_hospital_id(hospital_name):
    try:
        hospital = Hospital.objects.get(name=hospital_name)
        return hospital.id  # Return the hospital ID
    except Hospital.DoesNotExist:
        return None

def get_department_id(department_name):
    try:
        department = Department.objects.get(name=department_name)
        return department.id  # Return the department ID
    except Department.DoesNotExist:
        return None

def check_valid_pair(hospital_name, department_name):
    hospital, department = get_hospital_id(hospital_name), get_department_id(department_name)
    is_valid = HospitalDepartment.objects.filter(hospital=hospital, department=department).exists()
    return [hospital, department, is_valid]

class DoctorList(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(permission_required('doctor.view_doctor', raise_exception=True))
    def get(self, request):
        cached_data = cache.get('doctor_list')
        if cached_data is not None:
            return Response(cached_data, status=status.HTTP_200_OK)
        doctors = Doctor.objects.all()
        serializer = DoctorSerializer(doctors, many=True)
        cache.set('doctor_list', serializer.data, timeout=60*10)
        return Response(serializer.data)
    
    @method_decorator(permission_required('doctor.change_doctor', raise_exception=True))
    def post(self, request):
        body = json.loads(request.body)

        try:
            name, hospital_name, department_name = body["name"], body["hospital"], body["department"]
        except KeyError as e:
            return Response({"error": "Invalid request body "+str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        # retrieve hospital and department ids from name, ig they can conflict if two hospitals have same names
        hospital_id, department_id, is_valid_pair = check_valid_pair(hospital_name, department_name)
        if not is_valid_pair:
            return Response(
                {"error": f"The hospital '{hospital_name}' and department '{department_name}' are not linked."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get Hospital and Department instances from their IDs
        hospital = Hospital.objects.get(id=hospital_id)
        department = Department.objects.get(id=department_id)

        doctor = Doctor.objects.create(
            name=name,
            hospital=hospital,
            department=department
        )
        doctor_serializer = DoctorSerializer(doctor)
        return Response(doctor_serializer.data, status=status.HTTP_202_ACCEPTED)
    
class DoctorView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Doctor.objects.get(pk=pk)
        except Doctor.DoesNotExist:
            return None

    @method_decorator(permission_required('doctor.view_doctor', raise_exception=True))
    def get(self, request, pk):
        cached_data = cache.get(f'doctor_{pk}')
        if cached_data is not None:
            return Response(cached_data, status=status.HTTP_200_OK)
        doctor = self.get_object(pk)
        if not doctor:
            return Response(status.HTTP_400_BAD_REQUEST)
        serializer = DoctorSerializer(doctor)
        cache.set(f'doctor_{pk}', serializer.data, timeout=60*10)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @method_decorator(permission_required('doctor.change_doctor', raise_exception=True))
    def put(self, request, pk):
        body = json.loads(request.body)
        doctor = self.get_object(pk)
        if not doctor:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        try:
            name, hospital_name, department_name = body["name"], body["hospital"], body["department"]
        except KeyError as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)

        hospital, department, is_valid_pair = check_valid_pair(hospital_name, department_name)
        if not is_valid_pair:
            return Response(
                {"error": f"The hospital '{hospital_name}' and department '{department_name}' are not linked."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create validated data dictionary with IDs instead of names
        validated_data = {
            'name': name,
            'hospital': hospital,
            'department': department
        }
        
        serializer = DoctorSerializer(doctor, data=validated_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @method_decorator(permission_required('doctor.delete_doctor', raise_exception=True))
    def delete(self, request, pk):
        doctor = self.get_object(pk)
        if not doctor:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        doctor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
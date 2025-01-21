from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from .models import *
from .serializer import *
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.core.cache import cache
import json

class HospitalList(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(permission_required('hospital.view_hospital', raise_exception=True))
    def get(self, request):
        cached_data = cache.get('hospital_list')
        if cached_data is not None:
            return Response(cached_data, status=status.HTTP_200_OK)
        products = Hospital.objects.all()
        serializer = HospitalSerializer(products, many=True)
        cache.set('hospital_list', serializer.data, timeout=60*10)
        return Response(serializer.data)

    @method_decorator(permission_required('hospital.change_patient', raise_exception=True))
    def post(self, request):
        body = json.loads(request.body)
        hospital_name, department_names, addr = body["name"], body["departments"], None
        if "addr" in body: addr = body["addr"]
        
        # get or create hospital and departments
        try:
            hospital, hospital_created = Hospital.objects.get_or_create(name=hospital_name, defaults={"addr": addr})
            departments = []
            for name in department_names:
                department, _ = Department.objects.get_or_create(name=name)
                departments.append(department)
        except IntegrityError as e:
            return Response(f"{hospital_name} needs field \"addr\"", status=status.HTTP_400_BAD_REQUEST)

        # if hospital created, implies it is new, connect to all departments
        if hospital_created:
            HospitalDepartment.objects.bulk_create([
            HospitalDepartment(hospital=hospital, department=department) for department in departments])
            print(f"New hospital '{hospital_name}' added with departments: {department_names}")
        else:
            # __in is a field lookup used in Django's ORM to filter querysets based on whether a field's value is present in a list of values
            existing_departments = Department.objects.filter(
                id__in=HospitalDepartment.objects.filter(hospital=hospital).values_list('department_id', flat=True)
            )
            # the departments the existing hospital is not linked to, get them, and connect like before
            new_departments = [
                department for department in departments if department not in existing_departments
            ]

            HospitalDepartment.objects.bulk_create(
                [HospitalDepartment(hospital=hospital, department=department) for department in new_departments]
            )
        
        return Response("donezo", status=status.HTTP_200_OK)
    
class HospitalView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Hospital.objects.get(pk=pk)
        except Hospital.DoesNotExist:
            return None

    @method_decorator(permission_required('hospital.view_hospital', raise_exception=True))
    def get(self, request, pk):
        cached_data = cache.get(f'hospital_{pk}')
        if cached_data is not None:
            return Response(cached_data, status=status.HTTP_200_OK)
        hospital = self.get_object(pk)
        if not hospital:
            return Response(status.HTTP_400_BAD_REQUEST)
        serializer = HospitalSerializer(hospital)
        cache.set(f'hospital_{pk}', serializer.data, timeout=60*10)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # add hospital if it doesn't exist, if exists, add intersection of departments, if certain departments exist and hospital is new, make connection from existing departments to new hospital

    @method_decorator(permission_required('hospital.change_hospital', raise_exception=True))
    def put(self, request, pk):
        hospital = self.get_object(pk)
        if not hospital:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = HospitalSerializer(hospital, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @method_decorator(permission_required('hospital.delete_hospital', raise_exception=True))
    def delete(self, request, pk):
        hospital = self.get_object(pk)
        if not hospital:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        hospital.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class DepartmentList(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(permission_required('hospital.view_department', raise_exception=True))
    def get(self, request):
        cached_data = cache.get('department_list')
        if cached_data is not None:
            return Response(cached_data, status=status.HTTP_200_OK)
        products = Department.objects.all()
        serializer = DepartmentSerializer(products, many=True)
        cache.set('department_list', serializer.data, timeout=60*10)
        return Response(serializer.data)
    
class DepartmentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        try:
            return Department.objects.get(pk=pk)
        except Department.DoesNotExist:
            return None

    @method_decorator(permission_required('hospital.view_department', raise_exception=True))
    def get(self, request, pk):
        cached_data = cache.get(f'department_{pk}')
        if cached_data is not None:
            return Response(cached_data, status=status.HTTP_200_OK)
        department = self.get_object(pk)
        if not department:
            return Response(status.HTTP_400_BAD_REQUEST)
        serializer = DepartmentSerializer(department)
        cache.set(f'department_{pk}', serializer.data, timeout=60*10)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @method_decorator(permission_required('hospital.change_department', raise_exception=True))
    def put(self, request, pk):
        department = self.get_object(pk)
        if not department:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = DepartmentSerializer(department, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @method_decorator(permission_required('hospital.delete_department', raise_exception=True))
    def delete(self, request, pk):
        department = self.get_object(pk)
        if not department:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        department.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
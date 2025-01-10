from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from hospital.models import *
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
    def get(self, request):
        visits = Visit.objects.all()
        # replace all patient, hospital, department, doctor ids with actual names
        serializer = VisitSerializer(visits, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = VisitSerializer(data=request.data)
        # parse data, search for names and use ids
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

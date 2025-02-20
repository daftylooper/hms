from rest_framework import serializers
from .models import *
from rest_framework.response import Response
from rest_framework import status
from utils.crypto import CryptUtils
from dotenv import load_dotenv
from utils.crypto import CryptUtils
import re
import os

class PatientSerializer(serializers.ModelSerializer):
    cu = CryptUtils(os.getenv('DJANGO_SECRET_KEY'))
    class Meta:
        model = Patient
        fields = "__all__"

    def validate_phone(self, value):
        if Patient.objects.filter(phone=self.cu.encrypt(value)).exists():
            raise serializers.ValidationError("A patient with this phone number already exists.")
        return value

    def validate_email(self, value):
        if Patient.objects.filter(email=value).exists():
            raise serializers.ValidationError("A patient with this email already exists.")
        return value
    
    # encrypt phone number before saving the instance
    def create(self, validated_data):
        phone = validated_data.get('phone')
        if phone:
            validated_data['phone'] = self.cu.encrypt(str(phone))
        
        return super().create(validated_data)
    
    # same thing as create, but for update
    def update(self, instance, validated_data):
        phone = validated_data.get('phone')
        if phone:
            validated_data['phone'] = self.cu.encrypt(str(phone))
        
        return super().update(instance, validated_data)
    
    # decrypt phone number before returning the instance
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if 'phone' in data:
            # print("DA PHONE", data['phone'])
            data['phone'] = self.cu.decrypt(data['phone'])
        return data

class VisitSerializer(serializers.ModelSerializer):

    class Meta:
        model = Visit
        fields = "__all__"

    # validate the required or misspelled fields
    def validate(self, data):
        required_fields = ['patient', 'doctor', 'hospital', 'department']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise serializers.ValidationError(
                f"Missing/Mispelled required fields: {', '.join(missing_fields)}"
            )

        return data
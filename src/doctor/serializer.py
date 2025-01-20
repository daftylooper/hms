from rest_framework import serializers
from .models import Doctor

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = "__all__"
        extra_kwargs = {'allow_unknown': False}

    def validate(self, data):
        unknown_fields = set(self.initial_data.keys()) - set(self.fields.keys())
        if unknown_fields:
            raise serializers.ValidationError(
                f"Unknown field(s): {', '.join(unknown_fields)}"
            )
        return data
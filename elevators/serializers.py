from rest_framework import serializers
from .models import *

class LiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lift
        fields = "__all__"

class ElevatorSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElevatorSystem
        fields = "__all__"
    
class LiftRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiftRequest
        fields = "__all__"
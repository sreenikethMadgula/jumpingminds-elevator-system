from rest_framework import serializers
from .models import *

class LiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lift
        fields = "__all__"
    
    def create(self, validated_data):
        instance = self.Meta.model(**validated_data)
        if validated_data["out_of_order"]:
            instance.movement = False
            instance.door = False
            instance.current_floor = 0
        instance.save()
        return instance

class ElevatorSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElevatorSystem
        fields = "__all__"
    
class LiftRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiftRequest
        fields = "__all__"
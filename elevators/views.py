from .models import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import *
from .serializers import *

class HelloView(APIView):
    def get(self,req):
        res = Response()
        res.data = {
            "message": "Elevator System"
        }

class LiftList(APIView):
    def get(self,req):
        lifts = Lift.objects.all()
        serializer = LiftSerializer(lifts,many=True)
        return Response(serializer.data)

    # def post(self,req):
    #     serializer = LiftStatusSerializer(data=req.data)
    #     try:
    #         elevatorSystem = ElevatorSystem.objects.get(pk=1)
    #         max_lifts = elevatorSystem.lifts
    #     except:
    #         raise APIException("Elevator System not initialized")
    #     number_of_lifts = len(Lift.objects.all())
    #     if number_of_lifts == max_lifts:
    #         raise APIException("All lifts added. Can't add more")
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data,status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class LiftStatus(APIView):
    def get_lift_by_id(self,id):
        try:
            lift = Lift.objects.get(pk=id)
        except:
            raise NotFound("Invalid lift id")
        return lift
    def get(self,req,id):
        lift = self.get_lift_by_id(id)
        serializer = LiftSerializer(lift)
        data = {
            "message": "success",
            "data": serializer.data
        }
        return Response(data,status=status.HTTP_200_OK)
    
    def patch(self,req,id):
        lift = self.get_lift_by_id(id)
        serializer = LiftSerializer(lift,data=req.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            data = {
                "message": "success",
                "data": serializer.data
            }
            return Response(data,status=status.HTTP_205_RESET_CONTENT)
        return Response(serializer.erors,status=status.HTTP_400_BAD_REQUEST)


class InitializeView(APIView):
    def post(self, req):
        
        if len(ElevatorSystem.objects.all()) == 1:
            raise APIException("Already Initialized. You can try updating using PUT or PATCH")


        serializer = ElevatorSystemSerializer(data=req.data)
        max_lifts = req.data["lifts"]
        if max_lifts > 10:
            raise APIException("Can have a maximum of 10 lifts")
        if serializer.is_valid():
            serializers.save()
        else:
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
        for i in range(max_lifts):
            serializer = LiftSerializer(Lift())
            serializer.save()
        
        res = Response()
        res.data = {
            "message": "success",
            "data": serializer.data
        }

        return res
        
# class ElevatorSystemList(APIView):
#     def get(self,req):
#         elevatorSystems = ElevatorSystem.objects.all()
#         serializer = ElevatorSystemSerializer(elevatorSystems,many=True)
#         return Response(serializer.data,status=status.HTTP_200_OK)

class ElevatorSystemDetails(APIView):
    def get_elevator_system(self):
        try:
            elevatorSystem = ElevatorSystem.objects.get(pk=1)
        except:
            raise APIException("Elevator System not initialized.")
        
        return elevatorSystem

    def get(self,req):
        elevatorSystem = self.get_elevator_system()
        serializer = ElevatorSystemSerializer(elevatorSystem)
        data = {
            "message": "success",
            "data": serializer.data
        }
        return Response(data,status=status.HTTP_200_OK)
    
    def put(self,req):
        elevatorSystem = self.get_elevator_system()
        
        serializer = ElevatorSystemSerializer(elevatorSystem,data=req.data)

        if serializer.is_valid():
            serializer.save()
            data = {
                "message": "success",
                "data": serializer.data
            }
            return Response(data,status=status.HTTP_205_RESET_CONTENT)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def patch(self,req):
        elevatorSystem = self.get_elevator_system()

        serializer = ElevatorSystemSerializer(elevatorSystem,data=req.data,partial=True)

        if serializer.is_valid():
            serializer.save()
            data = {
                "message": "success",
                "data": serializer.data
            }
            return Response(data,status=status.HTTP_205_RESET_CONTENT)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
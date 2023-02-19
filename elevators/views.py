from .models import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import *
from .serializers import *
from .utils import *

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
    def get(self,req,id: int):
        lift = get_lift_from_id(id)
        serializer = LiftSerializer(lift)
        data = {
            "message": "success",
            "data": serializer.data
        }
        return Response(data,status=status.HTTP_200_OK)
    
    def put(self,req,id: int):
        lift = get_lift_from_id(id)
        serializer = LiftSerializer(lift,data=req.data)
        if serializer.is_valid():
            serializer.save()
            data = {
                "message": "success",
                "data": serializer.data
            }
            return Response(data,status=status.HTTP_205_RESET_CONTENT)
        return Response(serializer.erors,status=status.HTTP_400_BAD_REQUEST)

    def patch(self,req,id: int):
        lift = get_lift_from_id(id)
        serializer = LiftSerializer(lift,data=req.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            data = {
                "message": "success",
                "data": serializer.data
            }
            return Response(data,status=status.HTTP_205_RESET_CONTENT)
        return Response(serializer.erors,status=status.HTTP_400_BAD_REQUEST)


class LiftPositionsView(APIView):
    def get(self,req):
        elevator_system = get_elevator_system()
        # lifts = Lift.objects.all()
        floors = Lift.objects.all().only('current_field')
        lift_count = elevator_system.lifts
        lift_floor = {}
        for i in range(1,lift_count+1):
            lift_floor[i] = floors[i-1]
        data = {
            "message":"success",
            "description": "key: lift, value: current floor",
            "data": lift_floor
        }
        return Response(data,status=status.HTTP_200_OK)


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
            lift = Lift()
            serializer = LiftSerializer(lift)
            serializer.save()
            lift_request_obj = LiftRequest(lift,[])
            serializer = LiftRequestSerializer(lift_request_obj)
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
    def get(self,req):
        elevatorSystem = get_elevator_system()
        serializer = ElevatorSystemSerializer(elevatorSystem)
        data = {
            "message": "success",
            "data": serializer.data
        }
        return Response(data,status=status.HTTP_200_OK)
    
    def put(self,req):
        elevatorSystem = get_elevator_system()
        
        serializer = ElevatorSystemSerializer(elevatorSystem,data=req.data)

        if serializer.is_valid():
            serializer.save()
            data = {
                "message": "success",
                "data": serializer.data
            }
            set_lifts_to_default()
            return Response(data,status=status.HTTP_205_RESET_CONTENT)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def patch(self,req):
        elevatorSystem = get_elevator_system()

        serializer = ElevatorSystemSerializer(elevatorSystem,data=req.data,partial=True)

        if serializer.is_valid():
            serializer.save()
            data = {
                "message": "success",
                "data": serializer.data
            }
            set_lifts_to_default()
            return Response(data,status=status.HTTP_205_RESET_CONTENT)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class LiftRequestList(APIView):
    def get_lift_requests_by_lift_id(self,id: int):
        lift = get_lift_from_id(id)
        requests = LiftRequest.objects.filter(lift=lift)
        return requests
    def get(self,req,id: int):
        requests = self.get_lift_requests_by_lift_id(id)
        serializer = LiftRequestSerializer(requests, many=True)
        data = {
            "message": "success",
            "data": serializer.data
        }
        return Response(data,status=status.HTTP_200_OK)

class CallLiftView(APIView):
    def post(self,req):
        floor = req.data["floor"]
        elevatorSystem = get_elevator_system()
        max_floors = elevatorSystem.floors

        if floor > max_floors or floor < 0:
            raise APIException("Floor outside range")
        
        assigned_lift = assign_lift(floor)

        lift_request_obj = LiftRequest.objects.filter(lift=assigned_lift)
        lift_request_obj = update_destinations(lift_request_obj,floor)
        
        data = {
            "message": "success",
            "assigned_lift": assign_lift.id,
            "destinations": lift_request_obj.destinations
        }

        return Response(data)

class ChooseFloorView(APIView):
    def post(self,req,id):
        # user_current_floor = req.data["user_current_floor"]
        lift = get_lift_from_id(req.data["lift"])
        destination_floor = req.data["destination"]
        elevatorSystem = get_elevator_system()
        max_floors = elevatorSystem.floors
        if destination_floor > max_floors or destination_floor < 0:
            raise APIException("Floor outside range")
        
        # if lift.current_floor != user_current_floor:
        #     data = {
        #         "message": "Invalid request. Lift and user are on different floors"
        #     }
        #     return Response(data,status=status.HTTP_400_BAD_REQUEST)

        # lift_request_obj = get_lift_req_obj_from_lift(lift)

        # if not lift.door:
        #     data = {
        #         "message": "Invalid request. Must be inside lift to make choose floor. Door is closed"
        #     }
                
        
        # if lift.movement:
        #     data = {
        #         "message": "Invalid request. Lift is moving"
        #     }

        lift_request_obj = get_lift_req_obj_from_lift(lift)

        lift_request_obj = update_destinations(lift_request_obj,destination_floor)

        data = {
            "message": "success",
            "destinations": lift_request_obj.destinations
        }
            
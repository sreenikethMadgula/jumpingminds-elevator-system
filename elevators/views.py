from .models import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import *
from .serializers import *
from .utils import *

class HelloView(APIView):
    def get(self,req):
        set_lifts_to_default()
        res = Response()
        res.data = {
            "message": "Elevator System"
        }
        return res

class LiftList(APIView):
    def get(self,req):
        lifts = Lift.objects.all()
        serializer = LiftSerializer(lifts,many=True)
        return Response(serializer.data)

class LiftStatus(APIView):
    def get(self,req,id: int):
        elevator_system = get_elevator_system()
        lift = get_lift_from_id(id)
        serializer = LiftSerializer(lift)
        data = {
            "message": "success",
            "lift_status": serializer.data
        }
        return Response(data,status=status.HTTP_200_OK)

    def patch(self,req,id: int):
        elevator_system = get_elevator_system()

        lift = get_lift_from_id(id)
        try:
            ooo = req.data["out_of_order"]
        except:
            return Response(
                {
                    "message": "must have and can only change out_of_order field"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        # serializer = LiftSerializer(lift,data=req.data,partial=True)
        # if serializer.is_valid():
        #     serializer.save()
        #     data = {
        #         "message": "success",
        #         "data": serializer.data
        #     }
        #     return Response(data,status=status.HTTP_205_RESET_CONTENT)
        # return Response(serializer.erors,status=status.HTTP_400_BAD_REQUEST)
        lift.out_of_order = ooo
        serializer = LiftSerializer(data=lift)
        if serializer.is_valid():
            return Response(
                {
                    "message": "success",
                    "lift_status": serializer.data,
                    "movement": get_movement_string(lift)
                },
                status=status.HTTP_205_RESET_CONTENT
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LiftPositionsView(APIView):
    def get(self,req):
        elevator_system = get_elevator_system()
        lifts = Lift.objects.all()
        lift_floor = {}
        for lift in lifts:
            lift_floor["lift "+str(lift.id)] = "floor "+str(lift.current_floor)
        data = {
            "message":"success",
            # "description": "key: lift, value: current floor",
            "positions": lift_floor
        }
        return Response(data,status=status.HTTP_200_OK)


class InitializeView(APIView):
    def post(self, req):
        
        if len(ElevatorSystem.objects.all()) == 1:
            raise APIException("Already Initialized. You can try updating using PUT or PATCH")

        try:
            max_lifts = req.data["lifts"]
            max_floors = req.data["floors"]
        except:
            return Response(
                {
                    "message": "missing fields: lifts and/or floors"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if max_lifts > 10:
            raise APIException("Can have a maximum of 10 lifts")
        
        serializer = ElevatorSystemSerializer(data=req.data)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        for i in range(max_lifts):
            lift = {
                "movement":False,
                "out_of_order":False,
                "current_floor":0,
                "door":False
            }
            serializer = LiftSerializer(data=lift)
            if serializer.is_valid():
                lift = serializer.save()
                print("lift",lift.id)

            lift_request_obj = {
                "lift": lift.id,
                "destinations":[0]
            }
            serializer = LiftRequestSerializer(data=lift_request_obj)
            if serializer.is_valid():
                obj = serializer.save()
                print("obj", obj.id)
                obj = LiftRequest.objects.filter(lift=lift).first()
                obj.destinations = []
                obj.save()
                print("destinations",obj.destinations)
                serializer = LiftRequestSerializer(obj)
            else:
                print("error",serializer.errors)
        res = Response()
        res.data = {
            "message": "success",
            "elevator-system": serializer.data
        }

        return res
        

class ElevatorSystemDetails(APIView):
    def get(self,req):
        elevatorSystem = get_elevator_system()
        serializer = ElevatorSystemSerializer(elevatorSystem)
        data = {
            "message": "success",
            "elevator-system": serializer.data
        }
        return Response(data,status=status.HTTP_200_OK)
    
    def put(self,req):
        elevator_system = get_elevator_system()
        try:
            lifts = req.data["lifts"]
            floors = req.data["floors"]
        except:
            return Response(
                {
                    "message": "missing fields: lifts and/or floors"
                }
            )
        serializer = ElevatorSystemSerializer(elevator_system,data=req.data)
        if serializer.is_valid():
            serializer.save()
            data = {
                "message": "success",
                "elevator-system": serializer.data
            }
            if lifts>elevator_system.lifts:
                for i in range(elevator_system.lifts-lifts):
                    lift = {
                        "movement":False,
                        "out_of_order":False,
                        "current_floor":0,
                        "door":False
                    }
                    serializer = LiftSerializer(data=lift)
                    if serializer.is_valid():
                        lift = serializer.save()
                    lift_request_obj = {
                        "lift": lift.id,
                        "destinations":[0]
                    }
                    serializer = LiftRequestSerializer(data=lift_request_obj)
                    if serializer.is_valid():
                        serializer.save()                
            set_lifts_to_default()
            return Response(data,status=status.HTTP_205_RESET_CONTENT)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def patch(self,req):
        elevatorSystem = get_elevator_system()
        try:
            lifts = req.data["lifts"]
            if lifts>elevatorSystem.lifts:
                print("here")
                for i in range(lifts - elevatorSystem.lifts):
                    lift = {
                        "movement":False,
                        "out_of_order":False,
                        "current_floor":0,
                        "door":False
                    }

                    serializer = LiftSerializer(data=lift)
                    if serializer.is_valid():
                        lift = serializer.save()
                    lift_request_obj = {
                        "lift": lift.id,
                        "destinations":[0]
                    }
                    serializer = LiftRequestSerializer(data=lift_request_obj)
                    if serializer.is_valid():
                        serializer.save()
                    
            set_lifts_to_default()

        except Exception as e:
            print("this happened", e)
            pass
        serializer = ElevatorSystemSerializer(elevatorSystem,data=req.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            data = {
                "message": "success",
                "elevator-system": serializer.data
            }
            return Response(data,status=status.HTTP_205_RESET_CONTENT)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class LiftRequestList(APIView):
    def get_lift_requests_by_lift_id(self,id: int):
        lift = get_lift_from_id(id)
        requests = LiftRequest.objects.filter(lift=lift).first()
        return requests
    def get(self,req,id: int):
        elevator_system = get_elevator_system()
        requests = self.get_lift_requests_by_lift_id(id)
        serializer = LiftRequestSerializer(requests)
        print(serializer.data)
        data = {
            "message": "success",
            "data": serializer.data
        }
        return Response(data,status=status.HTTP_200_OK)

class CallLiftView(APIView):
    def post(self,req):
        elevatorSystem = get_elevator_system()
        try:
            floor = req.data["floor"]
        except:
            return Response(
                {
                    "message": "missing fields: floor"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        max_floors = elevatorSystem.floors

        if floor > max_floors or floor < 0:
            raise APIException("Floor outside range")
        
        assigned_lift = assign_lift(floor)
        destinations = get_lift_destinations(assigned_lift)
        if assigned_lift.current_floor == floor:
            assigned_lift.door = True
            assigned_lift.save()

        else:
            destinations = update_destinations(assigned_lift,floor)
            if len(destinations) == 1:
                if not assigned_lift.door:
                    destinations = go_to_next_destination(assigned_lift)
                    assigned_lift.door = True
        data = {
            "message": "success",
            "assigned_lift": assigned_lift.id,
            "destinations": destinations
        }

        return Response(data)

class ChooseFloorView(APIView):
    def post(self,req):
        elevatorSystem = get_elevator_system()

        try:
            lift_id = req.data["lift"]
            destination_floor = req.data["destination"]
        except:
            return Response(
                {
                    "message": "missing fields: lift and/or destination"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        max_floors = elevatorSystem.floors
        if destination_floor > max_floors or destination_floor < 0:
            raise APIException("Floor outside range")

        lift = get_lift_from_id(lift_id)
        destinations = update_destinations(lift,destination_floor)

        if lift.door:
            lift.door = False
            destinations = go_to_next_destination(lift)
            lift.door = True
        else:
            if len(destinations) == 1:
                destinations = go_to_next_destination(lift)
                lift.door = True
        data = {
            "message": "success",
            "lift": lift_id,
            "destinations": destinations
        }
        return Response(data)

class CloseDoorView(APIView):
    def post(self,req):
        elevator_system = get_elevator_system()
        try:
            lift_id = req.data["lift"]
        except:
            return Response(
                {
                    "message": "missing fields: lift"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        lift = get_lift_from_id(lift_id)
        if not lift.door:
            return Response(
                {
                    "message": "Door is already closed"
                }
            )
        lift.door = False
        
        destinations = get_lift_destinations(lift)
        if len(destinations) != 0:
            destinations = go_to_next_destination(lift)
            lift.door = True

        data = {
            "message": "success",
            "lift": lift_id,
            "destinations": destinations
        }
        return Response(data, status=status.HTTP_200_OK)
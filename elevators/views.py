from .models import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import *
from .serializers import *
from .utils import *

class HelloView(APIView):
    def get(self,req):
        elevator_system = get_elevator_system()
        # set_lifts_to_default()
        res = Response()
        res.data = {
            "message": "Elevator System"
        }
        return res

class ElevatorSystemDetails(APIView):
    def post(self, req):
        
        if len(ElevatorSystem.objects.all()) == 1:
            raise APIException("Already Initialized. You can DELETE and initialize again")

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
        
        initialize_lifts(max_lifts)
        res = Response()
        res.data = {
            "message": "success",
            "elevator-system": serializer.data
        }

        return res
        
    def get(self,req):
        elevator_system = get_elevator_system()
        serializer = ElevatorSystemSerializer(elevator_system)
        data = {
            "message": "success",
            "elevator-system": serializer.data
        }
        return Response(data,status=status.HTTP_200_OK)
    
    
    def delete(self,req):
        elevator_system = get_elevator_system()
        elevator_system.delete()
        Lift.objects.all().delete()
        return Response(
            {
                "message":"success"
            },
            status=status.HTTP_204_NO_CONTENT
        )

class LiftList(APIView):
    def get(self,req):
        lifts = Lift.objects.all()
        # serializer = LiftSerializer(lifts,many=True)
        data = []
        for lift in lifts:
            next_destination = None
            destinations = lift.destinations
            if len(destinations):
                next_destination = destinations[0]
            data.append(get_response_obj(lift,next_destination))
        print(data)
        return Response(data)

class LiftDetails(APIView):
    def get(self,req,id: int):
        elevator_system = get_elevator_system()
        lift = get_lift_from_id(id)
        destinations = lift.destinations
        serializer = LiftSerializer(lift)
        next_destination = None
        if len(destinations):
            next_destination = destinations[0]
        data = get_response_obj(lift,next_destination)
        return Response(data,status=status.HTTP_200_OK)

class LiftRequest(APIView):
    def get(self,req,id: int):
        elevator_system = get_elevator_system()
        lift = get_lift_from_id(id)
        destinations = lift.destinations
        next_destination = None
        if len(destinations):
            next_destination = destinations[0]
        data = get_response_obj(lift,next_destination)
        return Response(data,status=status.HTTP_200_OK)
    
    def patch(self, req, id: int):
        elevator_system = get_elevator_system()
        try:
            destination_floor = req.data["destination"]
        except:
            return Response(
                {
                    "message": "missing fields: destination"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        max_floors = elevator_system.floors
        if destination_floor > max_floors or destination_floor < 0:
            raise APIException("Floor outside range")

        lift = get_lift_from_id(id)
        check_out_of_order(lift)

        destinations = lift.destinations
        destinations = update_destinations(lift,destination_floor)

        if lift.door:
            lift.door = False
            destinations = go_to_next_destination(lift)
            lift.door = True
            lift.save()
        else:
            if len(destinations) == 1:
                destinations = go_to_next_destination(lift)
                lift.door = True
                lift.save()
        
        next_destination = None
        if len(destinations):
            next_destination=destinations[0]

        data = get_response_obj(lift,next_destination)
        return Response(data)

class LiftDoor(APIView):
    def get(self,req,id):
        elevator_system = get_elevator_system()
        lift = get_lift_from_id(id)
        data = {
            "message": "success",
            "lift":lift.id,
            "door":get_door_string(lift)
        }
    def patch(self,req,id: int):
        elevator_system = get_elevator_system()
        lift = get_lift_from_id(id)
        check_out_of_order(lift)
        try:
            door=req.data["door"]
        except:
            return Response(
                {
                    "message": "must have and can only change door field"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            lift.door = door
            lift.save()
            
            destinations = lift.destinations
            if door == False:
                if len(destinations) != 0:
                    destinations = go_to_next_destination(lift)
                    lift.door = True
                    lift.save()

            if len(destinations):
                next_destination = destinations[0]
            else:
                next_destination = None
            data = get_response_obj(lift,next_destination)
            return Response(
                data,
                status=status.HTTP_205_RESET_CONTENT
            )
        except:
            raise APIException("Failed due to internal server error")
    
class LiftMaintenance(APIView):
    def patch(self,req,id):
        elevator_system = get_elevator_system()
        lift = get_lift_from_id(id)

        try:
            ooo = req.data["out_of_order"]
        except:
            return Response(
                {
                    "message": "missing fields: out_of_order"
                    # "message": "must have and can change only 'out_of_order' field"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if lift.out_of_order != ooo:
            set_lift_to_default(lift)
        lift.out_of_order = ooo
        lift.save()
        data = get_response_obj(lift,None)
        return Response(
            data,
            status=status.HTTP_205_RESET_CONTENT
        )

class CallLiftView(APIView):
    def post(self,req):
        elevator_system = get_elevator_system()
        try:
            floor = req.data["floor"]
        except:
            return Response(
                {
                    "message": "missing fields: floor"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        max_floors = elevator_system.floors

        if floor > max_floors or floor < 0:
            raise APIException("Floor outside range")
        
        assigned_lift = assign_lift(floor)
        destinations = assigned_lift.destinations
        if assigned_lift.current_floor == floor:
            assigned_lift.door = True
            assigned_lift.save()

        else:
            destinations = update_destinations(assigned_lift,floor)
            if len(destinations) == 1:
                if assigned_lift.door == False:
                    destinations = go_to_next_destination(assigned_lift)
                    assigned_lift.door = True
                    assigned_lift.save()
        
        next_destination = None
        if len(destinations):
            next_destination=destinations[0]
        data = get_response_obj(assigned_lift,next_destination)

        return Response(data)
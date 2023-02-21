from .models import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import *
from .serializers import *
from .utils import *

from drf_yasg import openapi
# from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg.utils import swagger_auto_schema

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
    """
    Elevator System Details
    """
    @swagger_auto_schema(
        operation_summary="initialize elevator system",
        operation_description="initialize elevator system",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description='Number of floors and lifts',
            properties={
                'floors': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    # description='Inintialize'
                ),
                'lifts': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    # description='Inintialize'
                )
            }
        ),
    )
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
        
    @swagger_auto_schema(
        operation_summary="get elevator system details",
        operation_description="get elevator system details",
        operation_id="elevator-system_read"
    )
    def get(self,req):
        elevator_system = get_elevator_system()
        serializer = ElevatorSystemSerializer(elevator_system)
        data = {
            "message": "success",
            "elevator-system": serializer.data
        }
        return Response(data,status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary="delete elevator system",
        operation_description="delete elevator system",
    )
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
    """
    Lift list
    """
    @swagger_auto_schema(
        operation_summary="get lift list",
        operation_description="get lift list",
    )
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
    """
    Lift Details
    """
    @swagger_auto_schema(
        operation_summary="get lift details",
        operation_description="get lift details: door, current floor, destinations, next destination, movement, out of order",
    )
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
    """
    Lift requests
    """
    @swagger_auto_schema(
        operation_summary="get lift destinations",
        operation_description="get lift destinations",
    )
    def get(self,req,id: int):
        elevator_system = get_elevator_system()
        lift = get_lift_from_id(id)
        destinations = lift.destinations
        next_destination = None
        if len(destinations):
            next_destination = destinations[0]
        # data = get_response_obj(lift,next_destination)
        data = {
            "message": "success",
            "lift":lift.id,
            "destinations":lift.destinations
        }
        return Response(data,status=status.HTTP_200_OK)

    
    @swagger_auto_schema(
        operation_summary="choose destination floor from inside lift",
        operation_description="choose destination from inside lift",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description='destination floor',
            properties={
                'destination': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    default=0
                    # description='Inintialize'
                )
            }
        ),
    )
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
    """
    Lift door
    """
    @swagger_auto_schema(
        operation_summary="get lift door status",
        operation_description="get lift door status",
        operation_id="lift_door_read"
    )
    def get(self,req,id):
        elevator_system = get_elevator_system()
        lift = get_lift_from_id(id)
        data = {
            "message": "success",
            "lift":lift.id,
            "door":get_door_string(lift)
        }
    
    @swagger_auto_schema(
        operation_summary="open/close door",
        operation_description="open/close door",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description='false -> close door, true -> open door',
            properties={
                'door': openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    # description='Inintialize'
                )
            }
        ),
    )
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
    """
    Lift maintenance
    """
    @swagger_auto_schema(
        operation_summary="lift maintenance: mark lift out of order",
        operation_description="lift maintenance: mark lift out of order",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description='true -> out of order, false -> running',
            properties={
                'out_of_order': openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    default=False
                    # description='Inintialize'
                )
            }
        ),
    )
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
    @swagger_auto_schema(
        operation_summary="call lift at a specific floor",
        operation_description="call lift at a specific floor",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description='calling floor',
            properties={
                'floor': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    default=0
                    # description='Inintialize'
                )
            }
        ),
    )
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
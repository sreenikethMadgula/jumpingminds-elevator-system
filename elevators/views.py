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
        destinations = get_lift_destinations(lift)
        serializer = LiftSerializer(lift)

        if len(destinations):
            next_destination = destinations[0]
        else:
            next_destination = None
        data = {
            "message": "success",
            "lift_status": serializer.data,
            "destinations": destinations,
            "next_destination": next_destination,
            "movement": get_movement_string(lift)
        }
        return Response(data,status=status.HTTP_200_OK)

    def patch(self,req,id: int):
        try:
            elevator_system = get_elevator_system()

            lift = get_lift_from_id(id)
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
                
                destinations = get_lift_destinations(lift)
                if door == False:
                    if len(destinations) != 0:
                        destinations = go_to_next_destination(lift)
                        lift.door = True
                        lift.save()

                if len(destinations):
                    next_destination = destinations[0]
                else:
                    next_destination = None
                data = {
                    "message": "success",
                    "lift": lift.id,
                    "door": lift.door,
                    "current_floor": lift.current_floor,
                    "destinations": destinations,
                    "next_destination": next_destination,
                    "movement": get_movement_string(lift)
                }
                return Response(
                    data,
                    status=status.HTTP_205_RESET_CONTENT
                )
            except:
                raise APIException("Failed due to internal server error")
        except Exception as e:
            raise APIException(e)

        # try:
        #     ooo = req.data["out_of_order"]
        #     lift.out_of_order = ooo
        # except:
        #     # return Response(
        #     #     {
        #     #         "message": "must have and can only change out_of_order field"
        #     #     },
        #     #     status=status.HTTP_400_BAD_REQUEST
        #     # )
        #     pass
        

        # serializer = LiftSerializer(lift,data=req.data,partial=True)
        # if serializer.is_valid():
        #     return Response(
        #         {
        #             "message": "success",
        #             "lift_status": serializer.data,
        #             "movement": get_movement_string(lift)
        #         },
        #         status=status.HTTP_205_RESET_CONTENT
        #     )
        # return Response(
        #     serializer.errors,
        #     status=status.HTTP_400_BAD_REQUEST
        # )

class LiftMaintenance(APIView):
    def post(self,req,id):
        elevator_system = get_elevator_system()
        lift = get_lift_from_id(id)

        try:
            lift = req.data["lift"]
            ooo = req.data["out_of_order"]
        except:
            return Response(
                {
                    "message": "missing fields: lift and/or out_of_order"
                    # "message": "must have and can change only 'out_of_order' field"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        set_lift_to_default(lift)
        lift.out_of_order = ooo
        lift.save()
        lift_dict = {
                "id": lift.id,
                "door": lift.door,
                "current_floor": lift.current_floor,
                "out_of_order": lift.out_of_order,
            }
        serializer = LiftSerializer(data=lift_dict)
        if serializer.is_valid():
            return Response(
                {
                    "message":"success",
                    "lift": serializer.data
                }
            )
        return Response(
            serializer.errors,
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# class LiftPositionsView(APIView):
#     def get(self,req):
#         elevator_system = get_elevator_system()
#         lifts = Lift.objects.all()
#         lift_floor = {}
#         for lift in lifts:
#             lift_floor["lift "+str(lift.id)] = "floor "+str(lift.current_floor)
#         data = {
#             "message":"success",
#             # "description": "key: lift, value: current floor",
#             "positions": lift_floor
#         }
#         return Response(data,status=status.HTTP_200_OK)


class ElevatorSystemDetails(APIView):
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
                initialize_lifts(elevator_system.lifts - lifts)      
            return Response(data,status=status.HTTP_205_RESET_CONTENT)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def patch(self,req):
        elevator_system = get_elevator_system()
        try:
            lifts = req.data["lifts"]
            if lifts>elevator_system.lifts:
                initialize_lifts(elevator_system.lifts - lifts)
        except Exception as e:
            print("this happened", e)
            pass
        serializer = ElevatorSystemSerializer(elevator_system,data=req.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            data = {
                "message": "success",
                "elevator-system": serializer.data
            }
            return Response(data,status=status.HTTP_205_RESET_CONTENT)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,req):
        elevator_system = get_elevator_system()
        elevator_system.delete()
        return Response(
            {
                "message":"success"
            },
            status=status.HTTP_204_NO_CONTENT
        )

class LiftRequestDetails(APIView):
    def get(self,req,id: int):
        elevator_system = get_elevator_system()
        lift = get_lift_from_id(id)
        requests = get_lift_req_obj_from_lift(lift)
        serializer = LiftRequestSerializer(requests)
        print(serializer.data)
        data = {
            "message": "success",
            "data": serializer.data
        }
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
        data = {
            "message": "success",
            "lift": id,
            "destinations": destinations
        }
        return Response(data)


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
        destinations = get_lift_destinations(assigned_lift)
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
        data = {
            "message": "success",
            "assigned_lift": assigned_lift.id,
            "destinations": destinations
        }

        return Response(data)

# class ChooseFloorView(APIView):
#     def post(self,req):
#         elevator_system = get_elevator_system()

#         try:
#             lift_id = req.data["lift"]
#             destination_floor = req.data["destination"]
#         except:
#             return Response(
#                 {
#                     "message": "missing fields: lift and/or destination"
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         max_floors = elevator_system.floors
#         if destination_floor > max_floors or destination_floor < 0:
#             raise APIException("Floor outside range")

#         lift = get_lift_from_id(lift_id)
#         destinations = update_destinations(lift,destination_floor)

#         if lift.door:
#             lift.door = False
#             destinations = go_to_next_destination(lift)
#             lift.door = True
#         else:
#             if len(destinations) == 1:
#                 destinations = go_to_next_destination(lift)
#                 lift.door = True
#         data = {
#             "message": "success",
#             "lift": lift_id,
#             "destinations": destinations
#         }
#         return Response(data)

# class CloseDoorView(APIView):
#     def post(self,req):
#         elevator_system = get_elevator_system()
#         try:
#             lift_id = req.data["lift"]
#         except:
#             return Response(
#                 {
#                     "message": "missing fields: lift"
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         lift = get_lift_from_id(lift_id)
#         if not lift.door:
#             return Response(
#                 {
#                     "message": "Door is already closed"
#                 }
#             )
#         lift.door = False
        
#         destinations = get_lift_destinations(lift)
#         if len(destinations) != 0:
#             destinations = go_to_next_destination(lift)
#             lift.door = True

#         data = {
#             "message": "success",
#             "lift": lift_id,
#             "destinations": destinations
#         }
#         return Response(data, status=status.HTTP_200_OK)
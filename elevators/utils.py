from .models import *
from .serializers import *
from rest_framework.exceptions import *

def set_lift_to_default(lift: Lift):
    lift.out_of_order = False
    lift.door = False
    lift.current_floor = 0
    lift.destinations = []
    lift.save()

def set_lifts_to_default():
    lifts = Lift.objects.all()
    for lift in lifts:
        set_lift_to_default(lift)

def initialize_lifts(max_lifts):
    for i in range(max_lifts):
        lift = {
            "movement":False,
            "out_of_order":False,
            "current_floor":0,
            "door":False,
            "destinations":[0]
        }
        serializer = LiftSerializer(data=lift)
        if serializer.is_valid():
            lift = serializer.save()
            lift = Lift.objects.get(pk=lift.id)
            lift.destinations = []
            lift.save()


def get_elevator_system():
    elevatorSystem = ElevatorSystem.objects.all().first()
    try:
        elevatorSystem = ElevatorSystem.objects.get(pk=elevatorSystem.id)
    except:
        raise APIException("Elevator System not initialized.")
    
    return elevatorSystem

def get_lift_from_id(id: int):
    try:
        lift = Lift.objects.get(pk=id)
    except:
        raise NotFound("Invalid lift id")

    return lift

def get_lift_movement(lift: Lift):
    destinations = lift.destinations
    if len(destinations) == 0:
        return 0

    if lift.current_floor < destinations[0]:
        return 1
    
    return 2

def get_movement_string(lift: Lift):
    movement = get_lift_movement(lift)
    if movement == 0:
        return "STILL"
    if movement == 1:
        return "GOING UP"
    return "GOING DOWN"

def get_door_string(lift: Lift):
    door = lift.door
    if lift.door:
        return "OPEN"
    return 'CLOSED'

def get_lift_score(lift: Lift,floor):
    current_floor = lift.current_floor

    if floor == current_floor:
        return 0
    destinations = lift.destinations
    
    n = len(destinations)
    if n == 0:
        return abs(floor - current_floor)

    next_destination = destinations[0]
    if floor == next_destination:
        return abs(next_destination - floor)
    if (floor > current_floor and floor < next_destination) or (floor < current_floor and floor > next_destination):
        return abs(floor - current_floor)

    score = abs(next_destination - current_floor)
    i = 1
    while(i+1<n):
        current_floor = next_destination
        next_destination = destinations[i+1]
        if floor == next_destination:
            return score + abs(next_destination - floor)
        if (floor > current_floor and floor < next_destination) or (floor < current_floor and floor > next_destination):
            return score + abs(floor - current_floor)
        score += abs(next_destination-current_floor)
        i+=1
    score += abs(destinations[n-1] - floor)
    return score


def assign_lift(calling_floor: int):
    lifts = Lift.objects.filter(out_of_order=False)
    min_score = get_lift_score(lifts[0],calling_floor)
    assigned_lift = lifts[0]
    for lift in lifts:
        if lift.current_floor == calling_floor:
            if lift.door:
                return lift
        score = get_lift_score(lift,calling_floor)
        if score < min_score:
            min_score = score
            assigned_lift = lift

    return assigned_lift

def shitf_right(arr: list, pos: int):
    n = len(arr)
    i = n-1
    while i>pos:
        arr[i] = arr[i-1]
        i-=1
    return arr


def update_destinations(lift: Lift, floor):
    
    current_floor = lift.current_floor
    
    destinations = lift.destinations
    n = len(destinations)
    
    if floor == current_floor:
        return destinations

    if n == 0:
        destinations.append(floor)
        lift.destinations = destinations
        lift.save()
        return destinations


    next_destination = destinations[0]
    if n==1:
        if (floor > current_floor and floor < next_destination) or (floor < current_floor and floor > next_destination):
            destinations.append(next_destination)
            destinations[0] = floor
        else:
            destinations.append(floor)

        lift.destinations = destinations
        lift.save()
        return destinations

    if floor == current_floor:
        return destinations
    if (floor > current_floor and floor < next_destination) or (floor < current_floor and floor > next_destination):
        destinations.append(0)
        destinations = shitf_right(destinations,-1)
        destinations[0] = floor
        lift.destinations = destinations
        lift.save()
        return destinations


    i = 0
    while i+1<n:
        current_floor = destinations[i]
        next_destination = destinations[i+1]
        if floor == current_floor:
            return destinations
        if (floor > current_floor and floor < next_destination) or (floor < current_floor and floor > next_destination):
            destinations.append(0)
            destinations = shitf_right(destinations,i)
            destinations[i+1] = floor
            lift.destinations = destinations
            lift.save()
            return destinations
        i+=1
    if destinations[i]==floor:
        return destinations
    destinations.append(floor)
    lift.destinations = destinations
    lift.save()
    return destinations


def go_to_next_destination(lift: Lift):
    destinations = lift.destinations
    if len(destinations):
        lift.current_floor = destinations.pop(0)
        lift.destinations = destinations
        lift.save()

    return destinations
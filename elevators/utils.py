from .models import *
from rest_framework.exceptions import *

def set_lifts_to_default():
    lifts = Lift.objects.all()
    for lift in lifts:
        lift.movement = False
        lift.out_of_order = False
        lift.door = False
        lift.currentFloor = 0
        lift.save()

def get_elevator_system():
    try:
        elevatorSystem = ElevatorSystem.objects.get(pk=1)
    except:
        raise APIException("Elevator System not initialized.")
    
    return elevatorSystem

def get_lift_from_id(id: int):
    try:
        lift = Lift.objects.get(pk=id)
    except:
        raise NotFound("Invalid lift id")
    
    return lift

def get_lift_req_obj_from_lift(lift: Lift):
    return LiftRequest.objects.filter(lift=lift).first()

def get_lift_destinations(lift: Lift):
    obj = LiftRequest.objects.filter(lift=lift).first()
    return obj.destinations

def get_lift_score(lift: Lift,floor):
    current_floor = lift.current_floor

    if floor == current_floor and not lift.movement:
        return 0
    destinations = get_lift_destinations(lift)
    
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
    score += abs(destinations[n-1] - floor)
    return score


def assign_lift(calling_floor: int):
    # elevatorSystem = get_elevator_system()
    lifts = Lift.objects.all()
    # max_floors = elevatorSystem.floors
    min_score = get_lift_score(lifts[0])
    assigned_lift = lifts[0]
    # scores = {}
    for lift in lifts:
        score = get_lift_score(lift,calling_floor)
        # scores[lift.id] = score
        if score < min_score:
            min_score = score
            assigned_lift = lift

    return assigned_lift

def shitf_right(arr: list, pos: int):
    n = len(arr)
    i = n-1
    while i>pos:
        arr[i] = arr[i-1]


def update_destinations(lift: Lift, floor):
    lift_request_obj = get_lift_req_obj_from_lift(lift)
    destinations = lift_request_obj.destinations
    lift = Lift.objects.get(pk=lift_request_obj.lift.id)
    n = len(destinations)
    if n == 0:
        destinations.append(floor)
        lift_request_obj.destinations = destinations
        lift_request_obj.save()
        return destinations

    current_floor = lift.current_floor

    if n==1:
        next_destination = destinations[0]
        if (floor > current_floor and floor < next_destination) or (floor < current_floor and floor > next_destination):
            destinations.append(next_destination)
            destinations[0] = floor
            lift_request_obj.destinations = destinations
            lift_request_obj.save()
            return destinations
        
    i = 0
    while i+1<n:
        current_floor = destinations[i],
        next_destination = destinations[i+1]
        if (floor > current_floor and floor < next_destination) or (floor < current_floor and floor > next_destination):
            destinations.append(0)
            shitf_right(destinations,i)
            destinations[i] = floor
            lift_request_obj.destinations = destinations
            lift_request_obj.save()
            return destinations


def go_to_next_destination(lift: Lift):
    obj = get_lift_req_obj_from_lift(lift)
    destinations = obj.destinations
    if len(destinations):
        lift.current_floor = destinations.pop(0)
        obj.destinations = destinations
        obj.save()
        lift.save()

    return destinations
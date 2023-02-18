from django.db import models

# class ElevatorSystem(models.Model):


class Lift(models.Model):
    STILL=0
    UP=1
    DOWN=2
    movement_choices = [
        (STILL,"STILL"),
        (UP,"UP"),
        (DOWN,"DOWN")
    ]

    movement = models.IntegerField(
        max_length=1,
        choices=movement_choices,
        default=STILL
    )
    out_of_order = models.BooleanField(default=False)
    # True: open, False: closed
    door = models.BooleanField(default=False)
    currentFloor = models.IntegerField(default=0)

    elevatorSystem = models.ForeignKey(
        to='ElevatorSystem',
        on_delete=models.CASCADE
    )

class ElevatorSystem(models.Model):
    floors = models.IntegerField()
    lifts = models.IntegerField()

class LiftRequest(models.Model):
    lift = models.ForeignKey(
        to='Lift',
        on_delete=models.CASCADE
    )
    floor = models.IntegerField
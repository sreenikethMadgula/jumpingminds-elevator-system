from django.db import models
from django.contrib.postgres.fields import ArrayField
# class ElevatorSystem(models.Model):


class Lift(models.Model):
    out_of_order = models.BooleanField(default=False)
    # True: open, False: closed
    door = models.BooleanField(default=False)
    current_floor = models.IntegerField(default=0)
    destinations = ArrayField(
        models.IntegerField(
            blank=True,
            null=True
        )
    )
    # elevator_system = models.ForeignKey(
    #     to='ElevatorSystem',
    #     on_delete=models.CASCADE
    # )

class ElevatorSystem(models.Model):
    floors = models.IntegerField()
    lifts = models.IntegerField()

# class LiftRequest(models.Model):
#     lift = models.ForeignKey(
#         to='Lift',
#         on_delete=models.CASCADE
#     )
#     destinations = ArrayField(
#         models.IntegerField(
#             blank=True,
#             null=True
#         )
#     )
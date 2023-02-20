
from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('hello/',HelloView.as_view()),
    path('initialize/',InitializeView.as_view()),
    path('elevator-system-info/',ElevatorSystemDetails.as_view()),
    path('lifts/',LiftList.as_view()),
    path('lifts/<int:id>/status/',LiftStatus.as_view()),
    path('lifts/positions/', LiftPositionsView.as_view()),
    path('lifts/<int:id>/requests/',LiftRequestList.as_view()),
    path('call-lift/',CallLiftView.as_view()),
    path('choose-floor/',ChooseFloorView.as_view()),
    path('close-door/',CloseDoorView.as_view()),
]

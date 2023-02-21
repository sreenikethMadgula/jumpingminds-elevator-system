
from django.urls import path
from .views import *

urlpatterns = [
    # path('hello/',HelloView.as_view()),
    path('elevator-system/',ElevatorSystemDetails.as_view()),
    path('lift/',LiftList.as_view()),
    path('lift/<int:id>/',LiftDetails.as_view()),
    path('lift/<int:id>/requests/',LiftRequest.as_view()),
    path('lift/<int:id>/door/',LiftDoor.as_view()),
    path('lift/<int:id>/maintenance/',LiftMaintenance.as_view()),
    path('request/',CallLiftView.as_view()),
]



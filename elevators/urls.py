
from django.urls import path
from .views import *

urlpatterns = [
    path('hello/',HelloView.as_view()),
    path('elevator-system/',ElevatorSystemDetails.as_view()),
    # path('elevator-system/maintenance',LiftMaintenance.as_view()),
    path('lift/',LiftList.as_view()),
    path('lift/<int:id>/',LiftDetails.as_view()),
    path('lift/<int:id>/requests/',LiftRequest.as_view()),
    path('lift/<int:id>/door/',LiftDoor.as_view()),
    path('lift/<int:id>/maintenance/',LiftMaintenance.as_view()),
    path('request/',CallLiftView.as_view()),
    # path('/user/choose-floor/',ChooseFloorView.as_view()),
    # path('/user/close-door/',CloseDoorView.as_view()), # lift/id/close
]


# out of order -> elevator system
# door -> lift

# initialize elevator system -> post on /elevator-system/
# change elevator system -> PUT/PATCH on /elevator-system/

# close door, maintenance -> PATCH on /lift/<int:id>
# choose floor -> PATCH on /lift/<int:id>/requests/

# user namespace
# request lift -> POST on /user/request/

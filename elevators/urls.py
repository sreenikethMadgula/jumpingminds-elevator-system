
from django.urls import path
from .views import *

urlpatterns = [
    path('hello/',HelloView.as_view()),
    path('elevator-system/',ElevatorSystemDetails.as_view()),
    path('elevator-system/maintenance',ElevatorSystemDetails.as_view()),
    # path('elevator-system/maintenance/',)
    path('lift/',LiftList.as_view()),
    path('lift/<int:id>/',LiftStatus.as_view()),
    # path('lift/positions/', LiftPositionsView.as_view()),
    path('lift/<int:id>/requests/',LiftRequestDetails.as_view()),
    path('/request/',CallLiftView.as_view()),
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

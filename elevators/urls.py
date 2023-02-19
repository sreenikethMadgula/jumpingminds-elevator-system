
from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('hello/',HelloView.as_view()),
    path('initialize/',InitializeView.as_view()),
    path('elevator-system-info/',ElevatorSystemDetails.as_view()),
    path('lifts/',LiftList.as_view()),
    path('lifts/<int:id>',LiftStatus.as_view()),
    # path('call/<int:floor>')
]

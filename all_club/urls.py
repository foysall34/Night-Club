from django.urls import path
from .views import club_details

urlpatterns = [
    path("specific-club/<int:club_id>/", club_details, name="club-details"),
]

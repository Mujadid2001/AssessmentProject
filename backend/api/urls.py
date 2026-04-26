"""
Django URL configuration for ELD API
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DriverViewSet, TripViewSet, ELDLogViewSet

router = DefaultRouter()
router.register(r"drivers", DriverViewSet, basename="driver")
router.register(r"trips", TripViewSet, basename="trip")
router.register(r"logs", ELDLogViewSet, basename="log")

urlpatterns = [
    path("", include(router.urls)),
]

"""
Main URL configuration for ELD project
"""

from django.urls import path, include
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(["GET"])
def health_check(request):
    """Health check endpoint for deployment monitoring"""
    return Response(
        {
            "status": "healthy",
            "service": "ELD Simulator",
            "version": "1.0.0"
        }
    )

urlpatterns = [
    path("api/health/", health_check, name="health_check"),
    path("api/", include("api.urls")),
]

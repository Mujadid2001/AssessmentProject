"""
Django REST API views for ELD system using Service Layer pattern
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from django.utils import timezone
from datetime import datetime

from .models import Driver, Trip, ELDLog
from .serializers import (
    DriverSerializer,
    TripSerializer,
    ELDLogSerializer,
    GenerateLogsRequestSerializer,
    GenerateLogsResponseSerializer,
)
from services.hos_engine import HOSEngine, DutyStatus


class DriverViewSet(viewsets.ModelViewSet):
    """ViewSet for managing drivers"""

    queryset = Driver.objects.all()
    serializer_class = DriverSerializer

    @action(detail=True, methods=["get"])
    def cycle_status(self, request: Request, pk: int = None) -> Response:
        """Get driver's current HOS cycle status"""
        driver = self.get_object()
        hours_available = 70 - driver.cycle_hours_used
        return Response(
            {
                "driver_id": driver.id,
                "cycle_hours_used": driver.cycle_hours_used,
                "hours_available": hours_available,
                "cycle_start": driver.cycle_start,
                "requires_restart": driver.cycle_hours_used >= 70,
            }
        )


class TripViewSet(viewsets.ModelViewSet):
    """ViewSet for managing trips"""

    queryset = Trip.objects.all()
    serializer_class = TripSerializer

    def perform_create(self, serializer) -> None:
        """Override create to set default status"""
        serializer.save(status="PENDING")


class ELDLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing generated logs"""

    queryset = ELDLog.objects.all()
    serializer_class = ELDLogSerializer

    def get_queryset(self):
        """Filter logs by driver_id if provided"""
        queryset = ELDLog.objects.all()
        driver_id = self.request.query_params.get("driver_id")
        if driver_id:
            queryset = queryset.filter(driver_id=driver_id)
        return queryset

    @action(detail=False, methods=["post"])
    def generate_logs(self, request: Request) -> Response:
        """
        Generate HOS logs for a trip using the HOSEngine.
        
        This is the main endpoint for log generation with full HOS compliance.
        
        Request body:
        {
            "driver_id": int,
            "current_location": str,
            "pickup_location": str,
            "dropoff_location": str,
            "distance_miles": float,
            "cycle_used": float,
            "start_time": ISO8601 datetime
        }
        """
        serializer = GenerateLogsRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Extract validated data
            driver_id = serializer.validated_data["driver_id"]
            current_location = serializer.validated_data["current_location"]
            pickup_location = serializer.validated_data["pickup_location"]
            dropoff_location = serializer.validated_data["dropoff_location"]
            distance_miles = serializer.validated_data["distance_miles"]
            cycle_used = serializer.validated_data["cycle_used"]
            start_time = serializer.validated_data["start_time"]

            # Get or create driver
            driver, created = Driver.objects.get_or_create(
                id=driver_id,
                defaults={
                    "first_name": "Driver",
                    "last_name": f"#{driver_id}",
                    "license_number": f"DL-{driver_id}",
                },
            )

            # Create trip record
            trip = Trip.objects.create(
                driver=driver,
                current_location=current_location,
                pickup_location=pickup_location,
                dropoff_location=dropoff_location,
                distance_miles=distance_miles,
                start_time=start_time,
                status="IN_PROGRESS",
            )

            # Initialize HOS engine with current cycle state
            hos_engine = HOSEngine(
                current_cycle_hours=cycle_used, cycle_start=driver.cycle_start
            )

            # Generate logs
            daily_logs, cycle_state = hos_engine.generate_logs(
                current_location=current_location,
                pickup_location=pickup_location,
                dropoff_location=dropoff_location,
                distance_miles=distance_miles,
                start_datetime=start_time,
            )

            # Persist logs to database
            created_logs = []
            for daily_log in daily_logs:
                eld_log = ELDLog.objects.create(
                    driver=driver,
                    trip=trip,
                    log_date=daily_log.log_date,
                    events_json=daily_log.to_dict()["events"],
                    total_driving_minutes=daily_log.total_driving_minutes,
                    total_on_duty_minutes=daily_log.total_on_duty_minutes,
                    total_miles=daily_log.total_miles,
                    violations=daily_log.violations,
                )
                created_logs.append(eld_log)

            # Update driver cycle state
            driver.cycle_hours_used = cycle_state.cycle_hours_used
            driver.cycle_start = cycle_state.cycle_start_date
            driver.current_location = dropoff_location
            driver.save()

            # Update trip status
            trip.status = "COMPLETED"
            trip.end_time = daily_logs[-1].events[-1].timestamp if daily_logs else start_time
            trip.save()

            # Build response
            logs_serializer = ELDLogSerializer(created_logs, many=True)
            response_data = {
                "logs": logs_serializer.data,
                "cycle_state": {
                    "cycle_hours_used": cycle_state.cycle_hours_used,
                    "hours_available": cycle_state.hours_available,
                    "cycle_start_date": cycle_state.cycle_start_date.isoformat(),
                    "requires_restart": cycle_state.requires_restart,
                },
                "requires_restart": cycle_state.requires_restart,
                "trip_id": trip.id,
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Driver.DoesNotExist:
            return Response(
                {"error": "Driver not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

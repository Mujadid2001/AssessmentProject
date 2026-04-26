"""
Django REST serializers for ELD API
"""

from rest_framework import serializers
from .models import Driver, Trip, ELDLog


class DriverSerializer(serializers.ModelSerializer):
    """Serializer for Driver model"""

    class Meta:
        model = Driver
        fields = [
            "id",
            "first_name",
            "last_name",
            "license_number",
            "current_location",
            "cycle_hours_used",
            "cycle_start",
            "violations_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TripSerializer(serializers.ModelSerializer):
    """Serializer for Trip model"""

    class Meta:
        model = Trip
        fields = [
            "id",
            "driver",
            "current_location",
            "pickup_location",
            "dropoff_location",
            "distance_miles",
            "start_time",
            "end_time",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ELDLogSerializer(serializers.ModelSerializer):
    """Serializer for ELDLog model"""

    class Meta:
        model = ELDLog
        fields = [
            "id",
            "driver",
            "trip",
            "log_date",
            "events_json",
            "total_driving_minutes",
            "total_on_duty_minutes",
            "total_miles",
            "violations",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class GenerateLogsRequestSerializer(serializers.Serializer):
    """Serializer for generate-logs API request"""

    driver_id = serializers.IntegerField()
    current_location = serializers.CharField(max_length=255)
    pickup_location = serializers.CharField(max_length=255)
    dropoff_location = serializers.CharField(max_length=255)
    distance_miles = serializers.FloatField(min_value=0)
    cycle_used = serializers.FloatField(min_value=0)
    start_time = serializers.DateTimeField()

    def validate_distance_miles(self, value: float) -> float:
        """Validate distance is reasonable"""
        if value > 5000:
            raise serializers.ValidationError("Distance cannot exceed 5000 miles")
        return value


class GenerateLogsResponseSerializer(serializers.Serializer):
    """Serializer for generate-logs API response"""

    logs = ELDLogSerializer(many=True, read_only=True)
    cycle_state = serializers.DictField(read_only=True)
    requires_restart = serializers.BooleanField(read_only=True)
    trip_id = serializers.IntegerField(read_only=True)

"""
Django models for ELD system
"""

from django.db import models
from django.core.validators import MinValueValidator
from datetime import datetime


class Driver(models.Model):
    """Driver profile with HOS tracking"""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True)
    current_location = models.CharField(max_length=255, default="Unknown")
    cycle_hours_used = models.FloatField(default=0.0, validators=[MinValueValidator(0)])
    cycle_start = models.DateTimeField(default=datetime.now)
    violations_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Trip(models.Model):
    """Represents a single trip/shipment"""
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name="trips")
    current_location = models.CharField(max_length=255)
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    distance_miles = models.FloatField(validators=[MinValueValidator(0)])
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "Pending"),
            ("IN_PROGRESS", "In Progress"),
            ("COMPLETED", "Completed"),
        ],
        default="PENDING",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Trip from {self.pickup_location} to {self.dropoff_location}"


class ELDLog(models.Model):
    """24-hour electronic log (one per day)"""
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name="logs")
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="logs", null=True)
    log_date = models.DateField()
    events_json = models.JSONField(default=list)
    total_driving_minutes = models.IntegerField(default=0)
    total_on_duty_minutes = models.IntegerField(default=0)
    total_miles = models.FloatField(default=0.0)
    violations = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-log_date"]
        unique_together = ["driver", "log_date"]

    def __str__(self) -> str:
        return f"Log for {self.driver.first_name} on {self.log_date}"

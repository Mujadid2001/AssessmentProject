"""
Django admin configuration for ELD system
"""

from django.contrib import admin
from .models import Driver, Trip, ELDLog


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'license_number', 'cycle_hours_used', 'created_at')
    search_fields = ('first_name', 'last_name', 'license_number')
    list_filter = ('created_at', 'cycle_start')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('driver', 'pickup_location', 'dropoff_location', 'distance_miles', 'status', 'created_at')
    search_fields = ('pickup_location', 'dropoff_location', 'driver__first_name')
    list_filter = ('status', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ELDLog)
class ELDLogAdmin(admin.ModelAdmin):
    list_display = ('driver', 'log_date', 'total_driving_minutes', 'total_miles', 'created_at')
    search_fields = ('driver__first_name', 'driver__last_name')
    list_filter = ('log_date', 'created_at')
    readonly_fields = ('created_at',)

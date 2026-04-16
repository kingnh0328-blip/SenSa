from django.contrib import admin
from .models import GeoFence, Device


@admin.register(GeoFence)
class GeoFenceAdmin(admin.ModelAdmin):
    list_display = ["name", "zone_type", "risk_level", "is_active", "created_at"]
    list_filter = ["zone_type", "risk_level", "is_active"]


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = [
        "device_id",
        "device_name",
        "sensor_type",
        "x",
        "y",
        "status",
        "is_active",
    ]
    list_filter = ["sensor_type", "status", "is_active"]

from rest_framework import serializers
from .models import GeoFence, Device


class GeoFenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeoFence
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = "__all__"

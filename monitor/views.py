from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import GeoFence, Device
from .serializers import GeoFenceSerializer, DeviceSerializer


def map_view(request):
    """공장 지도 메인 화면"""
    return render(request, "monitor/map.html")


class GeoFenceViewSet(viewsets.ModelViewSet):
    """지오펜스 CRUD API"""

    queryset = GeoFence.objects.filter(is_active=True).order_by("-created_at")
    serializer_class = GeoFenceSerializer

    def destroy(self, request, *args, **kwargs):
        # 실제 삭제 대신 비활성화
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DeviceViewSet(viewsets.ModelViewSet):
    """센서 디바이스 CRUD API"""

    queryset = Device.objects.filter(is_active=True)
    serializer_class = DeviceSerializer

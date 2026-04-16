from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"geofence", views.GeoFenceViewSet, basename="geofence")
router.register(r"device", views.DeviceViewSet, basename="device")

urlpatterns = [
    path("", views.map_view, name="map"),
    path("api/", include(router.urls)),
]

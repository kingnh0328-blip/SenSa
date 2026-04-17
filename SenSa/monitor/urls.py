"""
monitor 앱 URL 설정

- 페이지 뷰: Django Template 기반 (관제 지도 화면)
- API 뷰: DRF ViewSet 기반 (지오펜스/장비/알람 CRUD + 지오펜스 내부 판별)
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import SensorDataView

# ============================================================
# DRF Router — CRUD API 자동 생성
# ============================================================
router = DefaultRouter()
router.register(r'geofence', views.GeoFenceViewSet, basename='geofence')
router.register(r'device',   views.DeviceViewSet,   basename='device')
router.register(r'alarm',    views.AlarmViewSet,    basename='alarm')
router.register(r'map',      views.MapImageViewSet, basename='map') 

# ============================================================
# URL 패턴
# ============================================================
urlpatterns = [
    # === 페이지 (Template) ===
    path('', views.map_view, name='monitor-map'),

    # === API (DRF) ===
    path('api/', include(router.urls)),

    # 지오펜스 내부 판별 전용 API (표준 CRUD 외 커스텀 액션)
    path('api/check-geofence/', views.CheckGeofenceView.as_view(), name='check-geofence'),
    
    path('api/sensor-data/', SensorDataView.as_view(), name='sensor-data'),
]

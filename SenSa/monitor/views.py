from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from django.contrib.auth.decorators import login_required

from .models import GeoFence, Device, Alarm, MapImage
from .serializers import GeoFenceSerializer, DeviceSerializer, AlarmSerializer, MapImageSerializer
from .geofence_service import (
    check_worker_in_geofences,
    create_sensor_alarm,
    create_combined_alarm,
)


@login_required(login_url='/accounts/login/')
def map_view(request):
    return render(request, 'monitor/map.html')


# ════════════════════════════════════════════
# GeoFence CRUD
# ════════════════════════════════════════════
class GeoFenceViewSet(viewsets.ModelViewSet):
    queryset          = GeoFence.objects.filter(is_active=True).order_by('-created_at')
    serializer_class  = GeoFenceSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ════════════════════════════════════════════
# Device CRUD
# ════════════════════════════════════════════
class DeviceViewSet(viewsets.ModelViewSet):
    queryset         = Device.objects.filter(is_active=True)
    serializer_class = DeviceSerializer


# ════════════════════════════════════════════
# 지오펜스 내부 판별 API
# POST /monitor/api/check-geofence/
# ════════════════════════════════════════════
class CheckGeofenceView(APIView):
    """
    요청 body 예시:
    {
      "workers": [
        {"worker_id": "worker_01", "name": "작업자 A", "x": 150, "y": 170},
        {"worker_id": "worker_02", "name": "작업자 B", "x": 350, "y": 280}
      ],
      "sensors": [
        {"device_id": "sensor_01", "sensor_type": "gas", "status": "danger", "detail": "CO 250ppm"}
      ]
    }
    응답 예시:
    {
      "alarms": [
        {
          "alarm_id": 3,
          "alarm_level": "danger",
          "alarm_type": "geofence_enter",
          "message": "작업자 A이(가) [위험구역 A]에 진입했습니다.",
          "worker_id": "worker_01",
          "geofence_name": "위험구역 A"
        }
      ],
      "workers_in_fences": [
        {"worker_id": "worker_01", "geofence_id": 1, "geofence_name": "위험구역 A"}
      ]
    }
    """

    def post(self, request):
        workers = request.data.get('workers', [])
        sensors = request.data.get('sensors', [])
        all_alarms = []

        # 1. 각 작업자 위치를 모든 지오펜스와 대조
        workers_in_fences = []  # 현재 지오펜스 안에 있는 작업자 정보

        for worker in workers:
            w_id   = worker.get('worker_id', '')
            w_name = worker.get('name', w_id)
            w_x    = float(worker.get('x', 0))
            w_y    = float(worker.get('y', 0))

            fence_results = check_worker_in_geofences(w_id, w_name, w_x, w_y)

            for fr in fence_results:
                all_alarms.append({
                    **fr,
                    "worker_id":   w_id,
                    "worker_name": w_name,
                })
                workers_in_fences.append({
                    "worker_id":    w_id,
                    "geofence_id":  fr["geofence_id"],
                    "geofence_name":fr["geofence_name"],
                    "zone_type":    fr["zone_type"],
                })

        # 2. 센서 상태 알람 처리
        for sensor in sensors:
            s_id     = sensor.get('device_id', '')
            s_type   = sensor.get('sensor_type', '')
            s_status = sensor.get('status', 'normal')
            s_detail = sensor.get('detail', '')

            alarm = create_sensor_alarm(s_id, s_type, s_status, s_detail)
            if alarm:
                all_alarms.append(alarm)

        # 3. 복합 위험 판별
        #    작업자가 지오펜스 안에 있고 + 해당 구역 근처 센서가 위험일 때
        danger_sensors = [s for s in sensors if s.get('status') in ('danger', 'caution')]

        if workers_in_fences and danger_sensors:
            for wf in workers_in_fences:
                for ds in danger_sensors:
                    try:
                        fence_obj = GeoFence.objects.get(id=wf['geofence_id'])
                        combined  = create_combined_alarm(
                            worker_id     = wf['worker_id'],
                            worker_name   = wf.get('worker_name', wf['worker_id']),
                            geofence      = fence_obj,
                            device_id     = ds.get('device_id', ''),
                            sensor_status = ds.get('status', ''),
                        )
                        all_alarms.append(combined)
                    except GeoFence.DoesNotExist:
                        pass

        return Response({
            "alarms":            all_alarms,
            "workers_in_fences": workers_in_fences,
            "alarm_count":       len(all_alarms),
        })


# ════════════════════════════════════════════
# 알람 조회 / 읽음 처리 API
# ════════════════════════════════════════════
class AlarmViewSet(viewsets.ReadOnlyModelViewSet):
    queryset         = Alarm.objects.all().order_by('-created_at')
    serializer_class = AlarmSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        # ?unread=true 파라미터로 읽지 않은 알람만 필터
        if self.request.query_params.get('unread') == 'true':
            qs = qs.filter(is_read=False)
        # 최근 50개만
        return qs[:50]

    @action(detail=True, methods=['patch'])
    def read(self, request, pk=None):
        """특정 알람 읽음 처리 — PATCH /monitor/api/alarm/{id}/read/"""
        alarm         = self.get_object()
        alarm.is_read = True
        alarm.save()
        return Response({'status': 'read', 'id': alarm.id})

    @action(detail=False, methods=['patch'])
    def read_all(self, request):
        """전체 알람 읽음 처리 — PATCH /monitor/api/alarm/read_all/"""
        Alarm.objects.filter(is_read=False).update(is_read=True)
        return Response({'status': 'all read'})

# ════════════════════════════════════════════
# 공장 평면도 이미지 CRUD
# ════════════════════════════════════════════
class MapImageViewSet(viewsets.ModelViewSet):
    """
    - POST /monitor/api/map/         : 새 지도 업로드
    - GET  /monitor/api/map/current/ : 현재 활성 지도 조회
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    queryset = MapImage.objects.all()
    serializer_class = MapImageSerializer

    def perform_create(self, serializer):
        # 새 지도 업로드 시 기존 활성 지도 비활성화 (하나만 활성)
        MapImage.objects.filter(is_active=True).update(is_active=False)
        serializer.save(is_active=True)

    @action(detail=False, methods=['get'])
    def current(self, request):
        """현재 활성 지도 조회"""
        current_map = MapImage.objects.filter(is_active=True).first()
        if current_map:
            serializer = self.get_serializer(current_map)
            return Response(serializer.data)
        return Response(
            {'detail': '업로드된 지도가 없습니다.'},
            status=status.HTTP_404_NOT_FOUND
        )
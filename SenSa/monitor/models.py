from django.db import models


ZONE_TYPE_CHOICES = [
    ('danger', '위험'),
    ('caution', '주의'),
    ('restricted', '출입금지'),
]

RISK_LEVEL_CHOICES = [
    ('low', '낮음'),
    ('medium', '보통'),
    ('high', '높음'),
    ('critical', '심각'),
]

SENSOR_TYPE_CHOICES = [
    ('gas', '가스'),
    ('power', '전력'),
    ('temperature', '온도'),
    ('motion', '동작'),
]

STATUS_CHOICES = [
    ('normal', '정상'),
    ('caution', '주의'),
    ('danger', '위험'),
]

ALARM_TYPE_CHOICES = [
    ('geofence_enter', '위험구역 진입'),
    ('sensor_caution', '센서 주의'),
    ('sensor_danger',  '센서 위험'),
    ('combined',       '복합 위험'),  # 진입 + 센서 동시
]

ALARM_LEVEL_CHOICES = [
    ('info',     '정보'),
    ('caution',  '주의'),
    ('danger',   '위험'),
    ('critical', '심각'),
]


class GeoFence(models.Model):
    """위험 구역 — polygon은 [[x,y], ...] 이미지 내부 좌표"""
    name        = models.CharField(max_length=100)
    zone_type   = models.CharField(max_length=20, choices=ZONE_TYPE_CHOICES, default='danger')
    description = models.TextField(blank=True, default='')
    risk_level  = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES, default='high')
    polygon     = models.JSONField(default=list)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.zone_type}] {self.name}"


class Device(models.Model):
    """센서 디바이스 — x, y는 이미지 내부 좌표"""
    device_id      = models.CharField(max_length=50, unique=True)
    device_name    = models.CharField(max_length=100)
    sensor_type    = models.CharField(max_length=20, choices=SENSOR_TYPE_CHOICES, default='gas')
    x              = models.FloatField(default=0)
    y              = models.FloatField(default=0)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='normal')
    last_value     = models.FloatField(null=True, blank=True)
    last_value_unit= models.CharField(max_length=20, blank=True, default='')
    is_active      = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.device_name} ({self.device_id})"


class Alarm(models.Model):
    """
    알람 기록
    - 작업자가 지오펜스에 진입했거나
    - 센서가 임계치를 초과했거나
    - 두 조건이 동시에 발생했을 때 생성
    """
    alarm_type  = models.CharField(max_length=30, choices=ALARM_TYPE_CHOICES)
    alarm_level = models.CharField(max_length=20, choices=ALARM_LEVEL_CHOICES, default='caution')

    # 관련 작업자 정보
    worker_id   = models.CharField(max_length=50, blank=True, default='')
    worker_name = models.CharField(max_length=100, blank=True, default='')
    worker_x    = models.FloatField(null=True, blank=True)
    worker_y    = models.FloatField(null=True, blank=True)

    # 관련 지오펜스
    geofence    = models.ForeignKey(
        GeoFence, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='alarms'
    )

    # 관련 센서
    device_id   = models.CharField(max_length=50, blank=True, default='')
    sensor_type = models.CharField(max_length=20, blank=True, default='')

    # 알람 메시지
    message     = models.TextField()

    # 읽음 여부
    is_read     = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.alarm_level}] {self.message[:40]}"

class SensorData(models.Model):
    """센서 측정값 히스토리"""
    device      = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='data')
    co          = models.FloatField(null=True, blank=True)
    h2s         = models.FloatField(null=True, blank=True)
    co2         = models.FloatField(null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='normal')
    timestamp   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.device.device_name} @ {self.timestamp}"
        
class MapImage(models.Model):
    """공장 평면도 이미지"""
    image       = models.ImageField(upload_to='maps/')
    name        = models.CharField(max_length=100, blank=True, default='지도')
    width       = models.IntegerField(default=0)
    height      = models.IntegerField(default=0)
    is_active   = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.name} ({self.width}x{self.height})"        
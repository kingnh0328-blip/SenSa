from django.db import models

ZONE_TYPE_CHOICES = [
    ("danger", "위험"),
    ("caution", "주의"),
    ("restricted", "출입금지"),
]

RISK_LEVEL_CHOICES = [
    ("low", "낮음"),
    ("medium", "보통"),
    ("high", "높음"),
    ("critical", "심각"),
]

SENSOR_TYPE_CHOICES = [
    ("gas", "가스"),
    ("power", "전력"),
    ("temperature", "온도"),
    ("motion", "동작"),
]

STATUS_CHOICES = [
    ("normal", "정상"),
    ("caution", "주의"),
    ("danger", "위험"),
]


class GeoFence(models.Model):
    """위험 구역 (지오펜스) - polygon은 [[x,y], ...] 이미지 내부 좌표"""

    name = models.CharField(max_length=100)
    zone_type = models.CharField(
        max_length=20, choices=ZONE_TYPE_CHOICES, default="danger"
    )
    description = models.TextField(blank=True, default="")
    risk_level = models.CharField(
        max_length=20, choices=RISK_LEVEL_CHOICES, default="high"
    )
    polygon = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.zone_type}] {self.name}"


class Device(models.Model):
    """센서 디바이스 - x, y는 이미지 내부 좌표"""

    device_id = models.CharField(max_length=50, unique=True)
    device_name = models.CharField(max_length=100)
    sensor_type = models.CharField(
        max_length=20, choices=SENSOR_TYPE_CHOICES, default="gas"
    )
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="normal")
    last_value = models.FloatField(null=True, blank=True)
    last_value_unit = models.CharField(max_length=20, blank=True, default="")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.device_name} ({self.device_id})"

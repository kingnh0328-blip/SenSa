from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    커스텀 유저 모델.

    AbstractUser를 상속하여 Django의 모든 인증 기능을 그대로 사용한다.
    username, password, email, first_name, last_name, is_active,
    is_staff, is_superuser, date_joined, last_login 등이 자동 제공된다.
    """
    ROLE_CHOICES = [
        ('operator', '운영자'),
        ('admin', '관리자'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='operator',
        verbose_name='역할',
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='소속 부서',
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        default='',
        verbose_name='연락처',
    )

    class Meta:
        db_table = 'accounts_user'
        verbose_name = '사용자'
        verbose_name_plural = '사용자 목록'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_admin_role(self):
        return self.role == 'admin'
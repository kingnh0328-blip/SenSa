from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


def index(request):
    """루트 URL — 로그인 상태에 따라 분기"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


@login_required
def dashboard(request):
    """메인 대시보드"""
    return render(request, 'dashboard.html', {
        'fastapi_ws_url': 'ws://localhost:8001/ws/sensors/',
    })


@login_required
def map_view(request):
    """지도 전체 화면"""
    return render(request, 'map.html', {
        'fastapi_ws_url': 'ws://localhost:8001/ws/sensors/',
    })
# apps/devices/views.py — 기존 API 뷰 아래에 추가

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


# =============================================
# 페이지 뷰 (Template 렌더링)
# =============================================

@login_required
def device_list_page(request):
    """센서 장비 목록 페이지"""
    devices = Device.objects.filter(is_active=True).order_by('device_id')
    return render(request, 'devices/device_list.html', {
        'devices': devices,
    })


@login_required
def device_detail_page(request, pk):
    """센서 장비 상세 페이지"""
    device = get_object_or_404(Device, pk=pk)
    recent_data = SensorData.objects.filter(device=device).order_by('-timestamp')[:20]
    return render(request, 'devices/device_detail.html', {
        'device': device,
        'recent_data': recent_data,
    })


@login_required
def device_create_page(request):
    """센서 장비 등록 페이지"""
    if request.method == 'POST':
        try:
            device = Device.objects.create(
                device_id=request.POST['device_id'],
                device_name=request.POST['device_name'],
                sensor_type=request.POST['sensor_type'],
                location_x=float(request.POST['location_x']),
                location_y=float(request.POST['location_y']),
            )
            messages.success(request, f'센서 "{device.device_name}"이(가) 등록되었습니다.')
            return redirect('device-list-page')
        except Exception as e:
            messages.error(request, f'등록 실패: {e}')

    return render(request, 'devices/device_form.html', {
        'form_title': '센서 등록',
        'sensor_types': Device.SENSOR_TYPES,
    })


@login_required
def device_edit_page(request, pk):
    """센서 장비 수정 페이지"""
    device = get_object_or_404(Device, pk=pk)

    if request.method == 'POST':
        try:
            device.device_name = request.POST['device_name']
            device.sensor_type = request.POST['sensor_type']
            device.location_x = float(request.POST['location_x'])
            device.location_y = float(request.POST['location_y'])
            device.save()
            messages.success(request, f'센서 "{device.device_name}"이(가) 수정되었습니다.')
            return redirect('device-detail-page', pk=pk)
        except Exception as e:
            messages.error(request, f'수정 실패: {e}')

    return render(request, 'devices/device_form.html', {
        'form_title': '센서 수정',
        'device': device,
        'sensor_types': Device.SENSOR_TYPES,
    })


@login_required
def device_delete(request, pk):
    """센서 장비 삭제 (소프트 삭제 — is_active=False)"""
    device = get_object_or_404(Device, pk=pk)
    if request.method == 'POST':
        device.is_active = False
        device.save()
        messages.success(request, f'센서 "{device.device_name}"이(가) 삭제되었습니다.')
    return redirect('device-list-page')
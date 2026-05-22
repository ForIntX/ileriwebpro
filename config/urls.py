"""
config/urls.py — Ana URL yapılandırması
"""
from django.contrib import admin
from django.urls import path, include
from core import views as core_views

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # ── API Endpointleri ──────────────────────────────────────────────── #
    # /api/checkin/, /api/queue/<token>/, /api/queue/call-next/, vb.
    path('api/', include('core.urls', namespace='core')),
    # /api/anamnez/start/, /api/anamnez/message/, /api/anamnez/finish/
    path('api/anamnez/', include('anamnez.urls', namespace='anamnez')),

    # ── Kiosk Sayfa Görünümleri ───────────────────────────────────────── #
    path('', core_views.kiosk_index, name='kiosk_index'),
    path('kiosk/checkin/', core_views.kiosk_checkin, name='kiosk_checkin'),
    path('kiosk/success/', core_views.kiosk_success, name='kiosk_success'),
    path('kiosk/queue/<uuid:token>/', core_views.kiosk_queue, name='kiosk_queue'),
    path('kiosk/anamnez/<uuid:token>/', core_views.kiosk_anamnez, name='kiosk_anamnez'),
    path('kiosk/qr/', core_views.kiosk_qr, name='kiosk_qr'),

    # ── Doktor Paneli Sayfa Görünümleri ───────────────────────────────── #
    path('panel/', core_views.panel_dashboard, name='panel_dashboard'),
    path('panel/display/', core_views.panel_display, name='panel_display'),
    path('panel/doctor/<int:doctor_id>/', core_views.panel_doctor, name='panel_doctor'),
]

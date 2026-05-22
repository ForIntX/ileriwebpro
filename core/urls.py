from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # ── API Endpointleri ─────────────────────────────────────────────────── #

    # Literal path'ler UUID pattern'den ÖNCE gelmeli
    path('queue/call-next/',     views.call_next,     name='call_next'),
    path('queue/call-specific/', views.call_specific, name='call_specific'),
    path('queue/complete/',      views.queue_complete, name='queue_complete'),
    path('queue/cancel/',        views.queue_cancel,   name='queue_cancel'),

    # Panel API
    path('panel/doctor/<int:doctor_id>/', views.panel_doctor_api, name='panel_doctor_api'),
    path('panel/display/',               views.panel_display_api, name='panel_display_api'),

    # Hasta check-in
    path('checkin/', views.checkin, name='checkin'),

    # Sıra durumu sorgulama (polling)
    path('queue/<uuid:queue_token>/', views.queue_status, name='queue_status'),
]

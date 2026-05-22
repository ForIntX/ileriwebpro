from django.urls import path
from . import views

app_name = 'anamnez'

urlpatterns = [
    # 4. Anamnez oturumu başlat
    path('start/', views.anamnez_start, name='start'),

    # 5. Hasta mesajını işle
    path('message/', views.anamnez_message, name='message'),

    # 6. Anamnezi bitir, özet üret
    path('finish/', views.anamnez_finish, name='finish'),
]

from django.contrib import admin
from .models import AnamnezRecord


@admin.register(AnamnezRecord)
class AnamnezRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'queue_entry', 'detected_category', 'risk_detected', 'created_at')
    list_filter = ('risk_detected', 'detected_category')
    search_fields = ('patient__full_name', 'detected_category', 'summary')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Bağlantı', {
            'fields': ('patient', 'queue_entry'),
        }),
        ('AI Analiz', {
            'fields': ('detected_category', 'risk_detected', 'summary'),
        }),
        ('Mesajlar (Ham Veri)', {
            'fields': ('messages',),
            'classes': ('collapse',),
        }),
        ('Zamanlama', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

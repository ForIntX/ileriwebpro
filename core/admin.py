from django.contrib import admin
from .models import Polyclinic, Patient, Doctor, QueueEntry, CheckInToken


@admin.register(Polyclinic)
class PolyclinicAdmin(admin.ModelAdmin):
    list_display = ('name', 'floor', 'is_active')
    list_filter = ('is_active', 'floor')
    search_fields = ('name', 'floor')
    list_editable = ('is_active',)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'masked_tc', 'created_at')
    search_fields = ('full_name', 'tc_no')
    readonly_fields = ('created_at', 'masked_tc')
    fields = ('full_name', 'tc_no', 'masked_tc', 'created_at')

    def masked_tc(self, obj):
        """TC'nin son 2 hanesini maskele: 123456789** """
        tc = obj.tc_no
        if tc and len(tc) == 11:
            return tc[:9] + '**'
        return tc
    masked_tc.short_description = 'TC No (Maskeli)'


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'polyclinic', 'room_number', 'is_active')
    list_filter = ('is_active', 'polyclinic')
    search_fields = ('full_name', 'room_number', 'polyclinic__name')
    list_editable = ('is_active',)


@admin.register(QueueEntry)
class QueueEntryAdmin(admin.ModelAdmin):
    list_display = ('queue_number', 'patient', 'polyclinic', 'doctor', 'status', 'created_at')
    list_filter = ('status', 'polyclinic', 'doctor')
    search_fields = ('patient__full_name', 'polyclinic__name', 'doctor__full_name')
    readonly_fields = ('public_token', 'created_at', 'called_at', 'completed_at')
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('patient', 'polyclinic', 'doctor', 'queue_number', 'status')
        }),
        ('Token & Zamanlama', {
            'fields': ('public_token', 'created_at', 'called_at', 'completed_at'),
            'classes': ('collapse',),
        }),
        ('AI Özeti', {
            'fields': ('anamnez_summary',),
            'classes': ('collapse',),
        }),
    )


@admin.register(CheckInToken)
class CheckInTokenAdmin(admin.ModelAdmin):
    list_display = ('token', 'is_used', 'expires_at', 'created_at')
    list_filter = ('is_used',)
    search_fields = ('token',)
    readonly_fields = ('created_at',)

import uuid
from django.db import models


class Polyclinic(models.Model):
    name = models.CharField(max_length=100)
    floor = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Poliklinik"
        verbose_name_plural = "Poliklinikler"


class Patient(models.Model):
    tc_no = models.CharField(max_length=11, unique=True)
    full_name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Hasta"
        verbose_name_plural = "Hastalar"


class Doctor(models.Model):
    full_name = models.CharField(max_length=120)
    polyclinic = models.ForeignKey(
        Polyclinic, on_delete=models.CASCADE, related_name='doctors'
    )
    room_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Doktor"
        verbose_name_plural = "Doktorlar"


class QueueEntry(models.Model):
    STATUS_CHOICES = (
        ('waiting', 'Bekliyor'),
        ('called', 'Çağrıldı'),
        ('completed', 'Tamamlandı'),
        ('cancelled', 'İptal Edildi'),
    )
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name='queue_entries'
    )
    polyclinic = models.ForeignKey(
        Polyclinic, on_delete=models.CASCADE, related_name='queue_entries'
    )
    doctor = models.ForeignKey(
        Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='queue_entries'
    )
    queue_number = models.PositiveIntegerField()
    public_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    anamnez_summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    called_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = "Sıra Kaydı"
        verbose_name_plural = "Sıra Kayıtları"

    def __str__(self):
        return f"{self.polyclinic.name} - Sıra: {self.queue_number} ({self.get_status_display()})"


class CheckInToken(models.Model):
    token = models.CharField(max_length=100, unique=True)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token: {self.token} (Used: {self.is_used})"

    class Meta:
        verbose_name = "Check-in Token"
        verbose_name_plural = "Check-in Tokenlar"

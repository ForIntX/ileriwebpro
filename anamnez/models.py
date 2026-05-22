from django.db import models
from core.models import Patient, QueueEntry


class AnamnezRecord(models.Model):
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name='anamnez_records'
    )
    queue_entry = models.OneToOneField(
        QueueEntry, on_delete=models.CASCADE, related_name='anamnez_record'
    )
    messages = models.JSONField(default=list)
    detected_category = models.CharField(max_length=50, blank=True)
    risk_detected = models.BooleanField(default=False)
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Anamnez - {self.patient.full_name}"

    class Meta:
        verbose_name = "Anamnez Kaydı"
        verbose_name_plural = "Anamnez Kayıtları"

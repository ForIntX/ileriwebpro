# PROMPT 01: Modeller, Admin ve Seed Data

## Mevcut Model Kodları (Kullanıcı Tarafından Onaylanmış)
Aşağıdaki modelleri EXACT olarak implemente et. Alan isimleri, tipler, ilişkiler ve seçenekler değiştirilemez.

### core/models.py
```python
import uuid
from django.db import models

class Polyclinic(models.Model):
    name = models.CharField(max_length=100)
    floor = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.name

class Patient(models.Model):
    tc_no = models.CharField(max_length=11, unique=True)
    full_name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.full_name

class Doctor(models.Model):
    full_name = models.CharField(max_length=120)
    polyclinic = models.ForeignKey(Polyclinic, on_delete=models.CASCADE, related_name='doctors')
    room_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.full_name

class QueueEntry(models.Model):
    STATUS_CHOICES = (
        ('waiting', 'Bekliyor'),
        ('called', 'Çağrıldı'),
        ('completed', 'Tamamlandı'),
        ('cancelled', 'İptal Edildi'),
    )
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='queue_entries')
    polyclinic = models.ForeignKey(Polyclinic, on_delete=models.CASCADE, related_name='queue_entries')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='queue_entries')
    queue_number = models.PositiveIntegerField()
    public_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    anamnez_summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    called_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        ordering = ['created_at']
    def __str__(self): return f"{self.polyclinic.name} - Sıra: {self.queue_number} ({self.get_status_display()})"

class CheckInToken(models.Model):
    token = models.CharField(max_length=100, unique=True)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"Token: {self.token} (Used: {self.is_used})"
```

### anamnez/models.py
```python
from django.db import models
from core.models import Patient, QueueEntry

class AnamnezRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='anamnez_records')
    queue_entry = models.OneToOneField(QueueEntry, on_delete=models.CASCADE, related_name='anamnez_record')
    messages = models.JSONField(default=list)
    detected_category = models.CharField(max_length=50, blank=True)
    risk_detected = models.BooleanField(default=False)
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return f"Anamnez - {self.patient.full_name}"
```

## Yapılacaklar
1. Yukarıdaki modelleri EXACT olarak `core/models.py` ve `anamnez/models.py` dosyalarına yaz.
2. `core/admin.py` ve `anamnez/admin.py` için profesyonel admin konfigürasyonu yaz:
   - QueueEntry: `readonly_fields = ('public_token', 'created_at', 'called_at', 'completed_at')`
   - Patient: TC maskeleme gösterimi (son 2 hane *** olsun)
   - Tüm modellerde `list_filter`, `search_fields` olacak
3. `config/settings.py`'ye `LANGUAGE_CODE = 'tr-tr'`, `TIME_ZONE = 'Europe/Istanbul'` ekle.
4. `INSTALLED_APPS` içinde `core` ve `anamnez` olacak.
5. Migration oluştur: `makemigrations` ve `migrate` komutlarını çalıştırabilecek şekilde hazırla.
6. **Seed Data Komutu**: `python manage.py seed_demo` komutu ile aşağıdaki demo veriyi oluşturacak custom management command yaz:
   - 3 Poliklinik: Dahiliye (Kat 2), Cerrahi (Kat 3), Acil (Kat 1)
   - 3 Doktor: Dr. Ayşe Demir (Dahiliye, Oda 205), Dr. Mehmet Kaya (Cerrahi, Oda 310), Dr. Zeynep Yılmaz (Acil, Oda 101)
   - Her poliklinik aktif, her doktor aktif.
7. `requirements.txt` oluştur: `Django>=4.2,<5.0`

## Önemli Notlar
- `public_token` editable=False olacak, admin panelde salt-okunur.
- `CheckInToken` şimdilik model olarak duracak (QR ikinci aşamada kullanılacak).
- `anamnez_summary` QueueEntry'de TextField(blank=True) olarak duracak, AI özet buraya yazılacak.

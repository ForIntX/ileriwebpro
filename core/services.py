"""
core/services.py — Hasta ve sıra servis katmanı
"""

from django.utils import timezone

from .models import Patient, Polyclinic, Doctor, QueueEntry


def checkin_patient(tc_no: str, full_name: str, polyclinic_id: int, doctor_id=None) -> dict:
    """
    Hasta check-in işlemi:
    1. Patient get_or_create (tc_no unique).
    2. Aynı gün + aynı poliklinikte son sıra numarasını bul, +1 artır.
    3. QueueEntry oluştur.
    4. doctor_id verilmişse ve aktifse ata.
    """
    polyclinic = Polyclinic.objects.get(pk=polyclinic_id, is_active=True)

    patient, _ = Patient.objects.get_or_create(
        tc_no=tc_no,
        defaults={'full_name': full_name}
    )

    # Bugünkü son sıra numarası
    today = timezone.now().date()
    last_entry = (
        QueueEntry.objects
        .filter(polyclinic=polyclinic, created_at__date=today)
        .order_by('-queue_number')
        .first()
    )
    queue_number = (last_entry.queue_number + 1) if last_entry else 1

    # Doktor ataması
    doctor = None
    if doctor_id:
        try:
            doctor = Doctor.objects.get(pk=doctor_id, is_active=True, polyclinic=polyclinic)
        except Doctor.DoesNotExist:
            doctor = None

    entry = QueueEntry.objects.create(
        patient=patient,
        polyclinic=polyclinic,
        doctor=doctor,
        queue_number=queue_number,
    )

    return {
        "queue_token": str(entry.public_token),
        "queue_number": entry.queue_number,
        "polyclinic": polyclinic.name,
        "doctor": doctor.full_name if doctor else None,
        "room": doctor.room_number if doctor else None,
    }


def get_queue_status(queue_token: str) -> dict:
    """
    Hasta sıra durumu:
    - remaining_count: Aynı poliklinikte, waiting, kendinden önce oluşturulmuş kayıt sayısı.
    - TC asla döndürülmez.
    """
    entry = QueueEntry.objects.select_related(
        'patient', 'polyclinic', 'doctor'
    ).get(public_token=queue_token)

    remaining_count = QueueEntry.objects.filter(
        polyclinic=entry.polyclinic,
        status='waiting',
        created_at__lt=entry.created_at,
    ).count()

    return {
        "patient_name": entry.patient.full_name,
        "queue_number": entry.queue_number,
        "remaining_count": remaining_count,
        "status": entry.status,
        "doctor_name": entry.doctor.full_name if entry.doctor else None,
        "room": entry.doctor.room_number if entry.doctor else None,
        "polyclinic": entry.polyclinic.name,
        "anamnez_summary": entry.anamnez_summary,
    }


def call_next_patient(doctor_id: int) -> dict:
    """
    Doktorun polikliniğindeki en eski 'waiting' hastayı çağırır.
    - Status → 'called', called_at → now(), doctor → bu doktor.
    """
    doctor = Doctor.objects.select_related('polyclinic').get(pk=doctor_id, is_active=True)

    entry = (
        QueueEntry.objects
        .filter(polyclinic=doctor.polyclinic, status='waiting')
        .order_by('created_at')
        .first()
    )
    if not entry:
        return None  # Görünümlerde 404 yapılacak

    entry.status = 'called'
    entry.doctor = doctor
    entry.called_at = timezone.now()
    entry.save(update_fields=['status', 'doctor', 'called_at'])

    return {
        "queue_token":     str(entry.public_token),
        "queue_number":    entry.queue_number,
        "patient_name":    entry.patient.full_name,
        "room":            doctor.room_number,
        "anamnez_summary": entry.anamnez_summary,
        "risk_detected":   bool(entry.anamnez_summary),  # Basit heuristik
    }


def call_specific_patient(entry_id: int, doctor_id: int) -> dict:
    """
    Belirli bir hastayı çağırır.
    """
    doctor = Doctor.objects.select_related('polyclinic').get(pk=doctor_id, is_active=True)
    entry  = QueueEntry.objects.select_related('patient').get(
        pk=entry_id, polyclinic=doctor.polyclinic, status='waiting'
    )

    entry.status    = 'called'
    entry.doctor    = doctor
    entry.called_at = timezone.now()
    entry.save(update_fields=['status', 'doctor', 'called_at'])

    return {
        "queue_token":     str(entry.public_token),
        "queue_number":    entry.queue_number,
        "patient_name":    entry.patient.full_name,
        "room":            doctor.room_number,
        "anamnez_summary": entry.anamnez_summary,
        "risk_detected":   bool(entry.anamnez_summary),
    }


def complete_patient(queue_token: str) -> None:
    """Çağrılan hastayı tamamlandı olarak işaretle."""
    entry = QueueEntry.objects.get(public_token=queue_token)
    entry.status       = 'completed'
    entry.completed_at = timezone.now()
    entry.save(update_fields=['status', 'completed_at'])


def cancel_patient(queue_token: str) -> None:
    """Hastayı iptal et."""
    entry = QueueEntry.objects.get(public_token=queue_token)
    entry.status = 'cancelled'
    entry.save(update_fields=['status'])


def get_doctor_panel_data(doctor_id: int) -> dict:
    """
    Doktor paneli için AJAX veri kaynağı.
    Bekleyen hastalar listesi + istatistikler.
    """
    doctor = Doctor.objects.select_related('polyclinic').get(pk=doctor_id, is_active=True)
    today  = timezone.now().date()
    qs     = QueueEntry.objects.filter(polyclinic=doctor.polyclinic, created_at__date=today)

    waiting = qs.filter(status='waiting').select_related('patient').order_by('created_at')

    waiting_list = [
        {
            "id":              e.id,
            "queue_number":    e.queue_number,
            "patient_name":    e.patient.full_name,
            "created_at":      e.created_at.isoformat(),
            "anamnez_summary": e.anamnez_summary,
            "risk_detected":   bool(e.anamnez_summary),
        }
        for e in waiting
    ]

    stats = {
        "waiting":   qs.filter(status='waiting').count(),
        "called":    qs.filter(status='called').count(),
        "completed": qs.filter(status='completed').count(),
        "total":     qs.count(),
    }

    return {
        "waiting_patients": waiting_list,
        "stats": stats,
    }


def get_display_data() -> dict:
    """
    Numaratör ekranı için son 5 çağrı.
    """
    today = timezone.now().date()
    calls = (
        QueueEntry.objects
        .filter(status__in=['called', 'completed'], created_at__date=today)
        .select_related('patient', 'polyclinic', 'doctor')
        .order_by('-called_at')[:5]
    )

    result = [
        {
            "id":           c.id,
            "queue_number": c.queue_number,
            "patient_name": c.patient.full_name,
            "polyclinic":   c.polyclinic.name,
            "doctor_name":  c.doctor.full_name if c.doctor else None,
            "room":         c.doctor.room_number if c.doctor else None,
            "called_at":    c.called_at.isoformat() if c.called_at else None,
        }
        for c in calls
    ]

    return {"recent_calls": result}

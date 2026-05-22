"""
anamnez/services.py — Anamnez servis katmanı
"""

from django.utils import timezone

from core.models import QueueEntry
from .models import AnamnezRecord
from . import ai_engine


def _get_queue_entry(queue_token: str) -> QueueEntry:
    """public_token UUID ile QueueEntry döndürür; bulunamazsa DoesNotExist fırlatır."""
    return QueueEntry.objects.select_related('patient', 'polyclinic', 'doctor').get(
        public_token=queue_token
    )


def start_anamnez(queue_token: str) -> dict:
    """
    Anamnez oturumunu başlatır.
    - QueueEntry'yi bul.
    - AnamnezRecord get_or_create.
    - İlk asistan mesajını ekle (eğer daha önce eklenmemişse).
    """
    entry = _get_queue_entry(queue_token)
    record, created = AnamnezRecord.objects.get_or_create(
        queue_entry=entry,
        defaults={'patient': entry.patient}
    )

    first_question = "Şikâyetiniz nedir?"

    if created or not record.messages:
        record.messages = [{"role": "assistant", "content": first_question}]
        record.save()

    return {"question": first_question}


def process_message(queue_token: str, user_message: str) -> dict:
    """
    Kullanıcı mesajını işler:
    1. Mesajı messages'e ekle.
    2. Kategori ve risk tespit et.
    3. Sonraki soruyu seç ve ekle.
    """
    entry = _get_queue_entry(queue_token)
    record = AnamnezRecord.objects.get(queue_entry=entry)

    # Kullanıcı mesajını kaydet
    messages = list(record.messages)
    messages.append({"role": "user", "content": user_message})

    # Kategori tespiti
    detected = ai_engine.detect_category(user_message)
    if detected != "general" and not record.detected_category:
        record.detected_category = detected

    effective_category = record.detected_category or "general"

    # Risk kontrolü
    if ai_engine.check_risk(user_message):
        record.risk_detected = True

    # Kaç asistan mesajı gönderildi?
    asked_count = sum(1 for m in messages if m.get("role") == "assistant")

    # Sonraki soruyu seç
    next_question = ai_engine.get_next_question(effective_category, asked_count)
    messages.append({"role": "assistant", "content": next_question})

    record.messages = messages
    record.save()

    return {
        "reply": next_question,
        "detected_category": effective_category,
        "risk_detected": record.risk_detected,
    }


def finish_anamnez(queue_token: str) -> dict:
    """
    Anamnezi bitirir, özet üretir ve her iki modele kaydeder.
    """
    entry = _get_queue_entry(queue_token)
    record = AnamnezRecord.objects.get(queue_entry=entry)

    summary = ai_engine.generate_summary(
        record.messages,
        record.detected_category or "general"
    )

    record.summary = summary
    record.save()

    # QueueEntry'ye de yaz (doktor panelinde kolay erişim)
    entry.anamnez_summary = summary
    entry.save(update_fields=['anamnez_summary'])

    return {"summary": summary}

"""
core/views.py — Kiosk & sıra yönetimi API + Page views

Tüm POST endpointler @csrf_exempt (kiosk cihazlardan API çağrısı için).
Tüm yanıtlar ortak {success, data/error, message} formatındadır.
"""

import json

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from . import services
from .models import Doctor, Polyclinic, QueueEntry


# --------------------------------------------------------------------------- #
#  Yardımcı                                                                   #
# --------------------------------------------------------------------------- #

def api_ok(data: dict, message: str = "İşlem başarılı.", status: int = 200) -> JsonResponse:
    return JsonResponse({"success": True, "data": data, "message": message}, status=status)


def api_err(error: str, status: int = 400) -> JsonResponse:
    return JsonResponse({"success": False, "error": error}, status=status)


def _parse_json(request) -> tuple[dict | None, JsonResponse | None]:
    try:
        return json.loads(request.body), None
    except (json.JSONDecodeError, ValueError):
        return None, api_err("Geçersiz JSON formatı.")


# =========================================================================== #
#  API ENDPOINTLERİ                                                            #
# =========================================================================== #

# --------------------------------------------------------------------------- #
#  1. POST /api/checkin/                                                       #
# --------------------------------------------------------------------------- #

@csrf_exempt
@require_http_methods(["POST"])
def checkin(request):
    body, err = _parse_json(request)
    if err:
        return err

    tc_no = (body.get("tc_no") or "").strip()
    full_name = (body.get("full_name") or "").strip()
    polyclinic_id = body.get("polyclinic_id")
    doctor_id = body.get("doctor_id")  # opsiyonel

    # --- Validasyonlar ---
    if not tc_no:
        return api_err("TC kimlik numarası boş olamaz.")
    if len(tc_no) != 11 or not tc_no.isdigit():
        return api_err("TC kimlik numarası tam 11 rakamdan oluşmalıdır.")
    if not full_name:
        return api_err("Ad soyad boş olamaz.")
    if not polyclinic_id:
        return api_err("Poliklinik seçilmedi.")

    try:
        data = services.checkin_patient(
            tc_no=tc_no,
            full_name=full_name,
            polyclinic_id=polyclinic_id,
            doctor_id=doctor_id,
        )
    except Exception as exc:
        return api_err(str(exc), status=400)

    return api_ok(data, message="Sıraya alındınız.", status=201)


# --------------------------------------------------------------------------- #
#  2. GET /api/queue/<uuid:queue_token>/                                       #
# --------------------------------------------------------------------------- #

@require_http_methods(["GET"])
def queue_status(request, queue_token):
    try:
        data = services.get_queue_status(str(queue_token))
    except Exception:
        return api_err("Sıra kaydı bulunamadı.", status=404)

    return api_ok(data)


# --------------------------------------------------------------------------- #
#  3. POST /api/queue/call-next/                                               #
# --------------------------------------------------------------------------- #

@csrf_exempt
@require_http_methods(["POST"])
def call_next(request):
    body, err = _parse_json(request)
    if err:
        return err

    doctor_id = body.get("doctor_id")
    if not doctor_id:
        return api_err("doctor_id zorunludur.")

    try:
        data = services.call_next_patient(int(doctor_id))
    except Exception as exc:
        return api_err(str(exc), status=400)

    if data is None:
        return api_err("Bekleyen hasta bulunamadı.", status=404)

    return api_ok(data, message="Hasta çağrıldı.")


# --------------------------------------------------------------------------- #
#  7. POST /api/queue/call-specific/  — Belirli hastayı çağır                 #
# --------------------------------------------------------------------------- #

@csrf_exempt
@require_http_methods(["POST"])
def call_specific(request):
    body, err = _parse_json(request)
    if err:
        return err

    entry_id  = body.get("entry_id")
    doctor_id = body.get("doctor_id")

    if not entry_id:
        return api_err("entry_id zorunludur.")
    if not doctor_id:
        return api_err("doctor_id zorunludur.")

    try:
        data = services.call_specific_patient(int(entry_id), int(doctor_id))
    except Exception as exc:
        return api_err(str(exc), status=400)

    return api_ok(data, message="Hasta çağrıldı.")


# --------------------------------------------------------------------------- #
#  8. POST /api/queue/complete/  — Hastayı tamamlandı yap                     #
# --------------------------------------------------------------------------- #

@csrf_exempt
@require_http_methods(["POST"])
def queue_complete(request):
    body, err = _parse_json(request)
    if err:
        return err

    queue_token = (body.get("queue_token") or "").strip()
    if not queue_token:
        return api_err("queue_token zorunludur.")

    try:
        services.complete_patient(queue_token)
    except Exception as exc:
        return api_err(str(exc), status=400)

    return api_ok({}, message="Hasta tamamlandı olarak işaretlendi.")


# --------------------------------------------------------------------------- #
#  9. POST /api/queue/cancel/  — Hastayı iptal et                             #
# --------------------------------------------------------------------------- #

@csrf_exempt
@require_http_methods(["POST"])
def queue_cancel(request):
    body, err = _parse_json(request)
    if err:
        return err

    queue_token = (body.get("queue_token") or "").strip()
    if not queue_token:
        return api_err("queue_token zorunludur.")

    try:
        services.cancel_patient(queue_token)
    except Exception as exc:
        return api_err(str(exc), status=400)

    return api_ok({}, message="Hasta iptal edildi.")


# --------------------------------------------------------------------------- #
#  10. GET /api/panel/doctor/<id>/  — Doktor paneli verileri (AJAX)           #
# --------------------------------------------------------------------------- #

@require_http_methods(["GET"])
def panel_doctor_api(request, doctor_id):
    try:
        data = services.get_doctor_panel_data(doctor_id)
    except Exception as exc:
        return api_err(str(exc), status=404)
    return api_ok(data)


# --------------------------------------------------------------------------- #
#  11. GET /api/panel/display/  — Numaratör son çağrılar                      #
# --------------------------------------------------------------------------- #

@require_http_methods(["GET"])
def panel_display_api(request):
    data = services.get_display_data()
    return api_ok(data)


# =========================================================================== #
#  PAGE VİEWS (HTML render)                                                   #
# =========================================================================== #

# --------------------------------------------------------------------------- #
#  Kiosk Ekranları                                                             #
# --------------------------------------------------------------------------- #

def kiosk_index(request):
    """GET /  → Kiosk ana ekran"""
    return render(request, "kiosk/index.html")


def kiosk_checkin(request):
    """GET /kiosk/checkin/ → Manuel check-in formu"""
    polyclinics = Polyclinic.objects.filter(is_active=True).order_by("name")
    doctors     = Doctor.objects.filter(is_active=True).select_related("polyclinic").order_by("full_name")
    return render(request, "kiosk/checkin.html", {
        "polyclinics": polyclinics,
        "doctors":     doctors,
    })


def kiosk_success(request):
    """GET /kiosk/success/?token=<uuid> → Başarılı sıra alma ekranı"""
    token = request.GET.get("token", "")
    context = {"token": token, "queue_number": "—", "polyclinic": "—"}

    if token:
        try:
            entry = QueueEntry.objects.select_related(
                "polyclinic", "doctor"
            ).get(public_token=token)
            context.update({
                "queue_number": entry.queue_number,
                "polyclinic":   entry.polyclinic.name,
                "doctor":       entry.doctor.full_name if entry.doctor else None,
                "room":         entry.doctor.room_number if entry.doctor else None,
            })
        except QueueEntry.DoesNotExist:
            pass

    return render(request, "kiosk/success.html", context)


def kiosk_queue(request, token):
    """GET /kiosk/queue/<uuid:token>/ → Sıra takip ekranı"""
    try:
        initial_data = services.get_queue_status(str(token))
    except Exception:
        initial_data = {
            "queue_number":   "—",
            "remaining_count": 0,
            "status":         "waiting",
            "doctor_name":    None,
            "room":           None,
            "polyclinic":     "—",
        }
    return render(request, "kiosk/queue.html", {
        "token":        str(token),
        "initial_data": initial_data,
        "room":         initial_data.get("room"),
    })


def kiosk_anamnez(request, token):
    """GET /kiosk/anamnez/<uuid:token>/ → Anamnez chat ekranı"""
    return render(request, "kiosk/anamnez.html", {"token": str(token)})


def kiosk_qr(request):
    """GET /kiosk/qr/ → QR giriş placeholder"""
    return render(request, "kiosk/qr.html")


# --------------------------------------------------------------------------- #
#  Panel Ekranları                                                             #
# --------------------------------------------------------------------------- #

def panel_dashboard(request):
    """GET /panel/ → Doktor paneli (ilk aktif doktor)"""
    doctor = Doctor.objects.filter(is_active=True).select_related("polyclinic").first()
    if doctor:
        return panel_doctor(request, doctor.id)
    # Doktor yoksa boş panel
    return render(request, "panel/doctor_dashboard.html", {
        "doctor": None,
        "all_doctors": [],
        "waiting_patients": [],
        "called_patient": None,
        "stats": {"waiting": 0, "called": 0, "completed": 0, "total": 0},
    })


def panel_doctor(request, doctor_id):
    """GET /panel/doctor/<id>/ → Belirli doktor paneli"""
    doctor      = get_object_or_404(Doctor, pk=doctor_id, is_active=True)
    all_doctors = Doctor.objects.filter(is_active=True).select_related("polyclinic")

    # Bugünkü istatistikler
    today = timezone.now().date()
    qs    = QueueEntry.objects.filter(
        polyclinic=doctor.polyclinic,
        created_at__date=today,
    )

    # Bekleyen ve çağrılan
    waiting_patients = qs.filter(status="waiting").select_related("patient").order_by("created_at")
    called_patient   = qs.filter(status="called").select_related("patient", "doctor").first()

    # Doktor başlıkları için waiting_count hesapla
    all_doctors_with_count = []
    for doc in all_doctors:
        doc.waiting_count = QueueEntry.objects.filter(
            polyclinic=doc.polyclinic, status="waiting",
            created_at__date=today,
        ).count()
        all_doctors_with_count.append(doc)

    stats = {
        "waiting":   qs.filter(status="waiting").count(),
        "called":    qs.filter(status="called").count(),
        "completed": qs.filter(status="completed").count(),
        "total":     qs.count(),
    }

    return render(request, "panel/doctor_dashboard.html", {
        "doctor":          doctor,
        "all_doctors":     all_doctors_with_count,
        "waiting_patients": waiting_patients,
        "called_patient":  called_patient,
        "stats":           stats,
    })


def panel_display(request):
    """GET /panel/display/ → Numaratör ekranı (genel, girişsiz)"""
    today        = timezone.now().date()
    recent_calls = (
        QueueEntry.objects
        .filter(status__in=["called", "completed"], created_at__date=today)
        .select_related("patient", "polyclinic", "doctor")
        .order_by("-called_at")[:5]
    )
    return render(request, "panel/queue_display.html", {
        "recent_calls": recent_calls,
    })

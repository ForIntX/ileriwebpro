"""
anamnez/views.py — Anamnez AI oturumu API endpoint'leri

Tüm POST endpointler @csrf_exempt.
"""

import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from . import services


# --------------------------------------------------------------------------- #
#  Yardımcı                                                                   #
# --------------------------------------------------------------------------- #

def api_ok(data: dict, message: str = "İşlem başarılı.", status: int = 200) -> JsonResponse:
    return JsonResponse({"success": True, "data": data, "message": message}, status=status)


def api_err(error: str, status: int = 400) -> JsonResponse:
    return JsonResponse({"success": False, "error": error}, status=status)


def _parse_json(request):
    try:
        return json.loads(request.body), None
    except (json.JSONDecodeError, ValueError):
        return None, api_err("Geçersiz JSON formatı.")


# --------------------------------------------------------------------------- #
#  4. POST /api/anamnez/start/                                                 #
# --------------------------------------------------------------------------- #

@csrf_exempt
@require_http_methods(["POST"])
def anamnez_start(request):
    body, err = _parse_json(request)
    if err:
        return err

    queue_token = (body.get("queue_token") or "").strip()
    if not queue_token:
        return api_err("queue_token zorunludur.")

    try:
        data = services.start_anamnez(queue_token)
    except Exception:
        return api_err("Sıra kaydı bulunamadı.", status=404)

    return api_ok(data, message="Anamnez başlatıldı.")


# --------------------------------------------------------------------------- #
#  5. POST /api/anamnez/message/                                               #
# --------------------------------------------------------------------------- #

@csrf_exempt
@require_http_methods(["POST"])
def anamnez_message(request):
    body, err = _parse_json(request)
    if err:
        return err

    queue_token = (body.get("queue_token") or "").strip()
    user_message = (body.get("message") or "").strip()

    if not queue_token:
        return api_err("queue_token zorunludur.")
    if not user_message:
        return api_err("Mesaj boş olamaz.")

    try:
        data = services.process_message(queue_token, user_message)
    except Exception as exc:
        return api_err(str(exc), status=404)

    return api_ok(data)


# --------------------------------------------------------------------------- #
#  6. POST /api/anamnez/finish/                                                #
# --------------------------------------------------------------------------- #

@csrf_exempt
@require_http_methods(["POST"])
def anamnez_finish(request):
    body, err = _parse_json(request)
    if err:
        return err

    queue_token = (body.get("queue_token") or "").strip()
    if not queue_token:
        return api_err("queue_token zorunludur.")

    try:
        data = services.finish_anamnez(queue_token)
    except Exception as exc:
        return api_err(str(exc), status=404)

    return api_ok(data, message="Özet doktor paneline iletildi.")

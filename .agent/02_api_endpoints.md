# PROMPT 02: API Endpoints ve Servis Katmanı

## Genel API Formatı (KESİN)
Başarılı:
```json
{"success": true, "data": {...}, "message": "İşlem başarılı."}
```
Hatalı:
```json
{"success": false, "error": "Hata mesajı"}
```

## Implemente Edilecek Endpointler

### 1. POST /api/checkin/
**Amaç**: Hasta check-in, sıra numarası oluşturma.

Request:
```json
{
  "tc_no": "12345678901",
  "full_name": "Ahmet Yılmaz",
  "polyclinic_id": 1,
  "doctor_id": 1
}
```

Validasyonlar:
- TC boş olamaz.
- TC tam 11 hane olmalı, sadece rakam.
- Poliklinik seçilmemişse hata.
- `full_name` boş olamaz.

Response (Başarılı):
```json
{
  "success": true,
  "data": {
    "queue_token": "uuid-token",
    "queue_number": 24,
    "polyclinic": "Dahiliye",
    "doctor": "Dr. Ayşe Demir",
    "room": "205"
  },
  "message": "Sıraya alındınız."
}
```

Servis Mantığı (`core/services.py`):
- Patient `get_or_create` (tc_no unique).
- Aynı gün içinde aynı poliklinik için son sıra numarasını bul, +1 artır.
- `QueueEntry` oluştur, `public_token` otomatik UUID.
- Eğer `doctor_id` verilmişse ve o doktor aktifse ata, yoksa boş bırak.

### 2. GET /api/queue/<uuid:queue_token>/
**Amaç**: Hasta sıra durumunu sorgulama (polling için kullanılacak).

Response:
```json
{
  "success": true,
  "data": {
    "patient_name": "Ahmet Yılmaz",
    "queue_number": 24,
    "remaining_count": 5,
    "status": "waiting",
    "doctor_name": "Dr. Ayşe Demir",
    "room": "205",
    "polyclinic": "Dahiliye",
    "anamnez_summary": "Hasta baş ağrısı şikâyeti bildirdi."
  }
}
```

Servis Mantığı:
- `remaining_count`: Aynı poliklinikte, `waiting` statusunde, kendinden önce oluşturulmuş kayıtların sayısı.
- `patient_name` yerine maskeleme opsiyonel (şimdilik tam isim dönebilir ama TC asla dönmeyecek).

### 3. POST /api/queue/call-next/
**Amaç**: Doktor bir sonraki hastayı çağırır.

Request:
```json
{"doctor_id": 1}
```

Validasyon:
- `doctor_id` zorunlu.
- Doktor aktif mi kontrol et.

Response:
```json
{
  "success": true,
  "data": {
    "queue_number": 24,
    "patient_name": "Ahmet Yılmaz",
    "room": "205"
  },
  "message": "Hasta çağrıldı."
}
```

Servis Mantığı:
- Doktorun polikliniğindeki en eski `waiting` hastayı bul (`order_by('created_at')`).
- Status'u `called` yap.
- `doctor` alanını bu doktora ata (eğer boşsa).
- `called_at` = now().
- Bekleyen hasta yoksa 404 döndür.

### 4. POST /api/anamnez/start/
**Amaç**: AI anamnez oturumunu başlat.

Request:
```json
{"queue_token": "uuid-token"}
```

Response:
```json
{
  "success": true,
  "data": {"question": "Şikâyetiniz nedir?"},
  "message": "Anamnez başlatıldı."
}
```

Servis Mantığı (`anamnez/services.py`):
- QueueEntry bul, yoksa 404.
- `AnamnezRecord` get_or_create (queue_entry OneToOne).
- İlk mesajı `messages` JSONField'a ekle: `{"role": "assistant", "content": "Şikâyetiniz nedir?"}`.
- Kaydet ve soruyu döndür.

### 5. POST /api/anamnez/message/
**Amaç**: Hasta cevabını işle, AI yanıt üret.

Request:
```json
{
  "queue_token": "uuid-token",
  "message": "Başım ağrıyor ve midem bulanıyor."
}
```

Response:
```json
{
  "success": true,
  "data": {
    "reply": "Bu şikâyet ne zamandır devam ediyor?",
    "detected_category": "headache",
    "risk_detected": false
  }
}
```

Servis Mantığı:
- AnamnezRecord bul.
- Kullanıcı mesajını `messages`'e ekle (`role: user`).
- `ai_engine.detect_category(message)` çağrısı ile kategori bul.
- Eğer kategori `general` değilse ve daha önce kategori atanmamışsa `detected_category`'ye kaydet.
- `ai_engine.check_risk(message)` çağrısı ile risk kontrolü yap. Risk varsa `risk_detected = True`.
- `ai_engine.get_next_question(category, asked_count)` ile sonraki soruyu seç.
  - `asked_count`: Record'taki `role: assistant` mesaj sayısı.
- Asistan mesajını `messages`'e ekle.
- Kaydet ve dön.

### 6. POST /api/anamnez/finish/
**Amaç**: Anamnez'i bitir, özet oluştur, doktor paneline ilet.

Request:
```json
{"queue_token": "uuid-token"}
```

Response:
```json
{
  "success": true,
  "data": {
    "summary": "Hastanın ana şikâyeti baş ağrısıdır. Şikâyet bu sabahtan beri devam etmektedir."
  },
  "message": "Özet doktor paneline iletildi."
}
```

Servis Mantığı:
- AnamnezRecord bul.
- `ai_engine.generate_summary(messages, detected_category)` çağrısı.
- Summary'yi `AnamnezRecord.summary`'ye kaydet.
- Aynı summary'yi `QueueEntry.anamnez_summary`'ye de kaydet (doktor panelinde kolay erişim için).
- `QueueEntry`'yi kaydet.

## URL Routing
- `config/urls.py`: `path('api/', include('core.urls'))`, `path('api/', include('anamnez.urls'))`
- `core/urls.py`: checkin, queue/<token>, call-next
- `anamnez/urls.py`: anamnez/start, anamnez/message, anamnez/finish

## CSRF
- Tüm POST endpointler `@csrf_exempt` olacak (kiosk ve harici cihazlardan API çağrısı için).

## Hata Yönetimi
- `get_object_or_404` kullan, yakalanmazsa 404 dönsün.
- `json.loads` hatası için try-except.
- Her hata `api_response(success=False, error=..., status=...)` formatında dönecek.

# PROMPT 05: Doktor Paneli ve Numarator Ekrani

## Tasarim Ilkeleri
- Doktor paneli: Laptop/desktop odakli, temiz tablolar.
- Numarator ekrani: Buyuk ekran/TV icin optimize, cok buyuk font, yuksek kontrast.

## Ekranlar

### 1. templates/panel/doctor_dashboard.html — Doktor Paneli
- URL: `/panel/doctor/<doctor_id>/` veya `/panel/dashboard/`
- Ust bilgi: Doktor adi, Poliklinik, Oda.
- **Bekleyen Hasta Listesi** (tablo):
  - Sira No | Hasta Adi | Giris Saati | Anamnez Ozeti | Buton
  - Buton: "Cagir"
- **Cagrilan Hasta** (ayri bolum, buyuk gosterim):
  - Su an cagrilan hasta bilgisi (Sira No, Ad, Anamnez Ozeti).
  - Butonlar: "Tamamlandi", "Iptal", "Sonraki Hasta"
- Anamnez ozeti varsa:
  - Ayri bir kart/bolumde goster.
  - Riskli ise kirmizi border/uyari ikonu.

### 2. templates/panel/queue_display.html — Genel Numarator Ekrani
- URL: `/panel/display/` (herkese acik, girissiz)
- Buyuk ekran/TV icin:
  - Son cagrilan 5 hasta listesi (buyuk font).
  - Her satir: Sira No | Poliklinik | Doktor | Oda
  - Yeni cagrilan hasta: 3 saniye flash animasyonu (sari arka plan).
  - Otomatik polling: 5 saniyede bir guncelleme.
  - Sesli uyari: Yeni hasta cagrildiginda basit beep (Web Audio API).

## API Entegrasyonu
- Doktor "Cagir" butonu -> POST /api/queue/call-next/ (doctor_id ile).
- Basarili yanit gelince:
  - Cagrilan hasta bolumu guncellenir.
  - Numarator ekrani otomatik guncellenir (polling).
- "Tamamlandi" butonu -> QueueEntry status = 'completed', completed_at = now.
- "Iptal" butonu -> QueueEntry status = 'cancelled'.

## views.py Mantigi
- Doktor paneli view'lari `core/views.py`'de veya ayri `panel/views.py`'de olabilir.
- Simdilik `core/views.py` icinde tut, proje tek app mantiginda.
- `@login_required` ekle (Django auth kullan).

## URL'ler
- `/panel/` -> Dashboard
- `/panel/display/` -> Genel numarator ekrani
- `/panel/doctor/<id>/` -> Belirli doktor paneli (opsiyonel)

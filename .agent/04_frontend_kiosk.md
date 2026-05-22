# PROMPT 04: Hasta Frontend Ekranlari (Kiosk)

## Tasarim Ilkeleri
- Kiosk ekranlarinda BUYUK BUTONLAR, AZ METIN, SADE TASARIM.
- Dokunmatik ekran icin optimize (buton min-height: 60px, font-size: 18px+).
- Bootstrap 5 veya pure CSS kullan (harici CDN'den yukle, local dosya bagimliligi olmasin).
- Responsive ama primarily tablet/dokunmatik ekran odakli.

## Ekranlar

### 1. templates/kiosk/index.html — Kiosk Ana Ekran
- Baslik: "Hastane Kiosk Sistemi"
- Iki buyuk buton:
  - "Sira Al (Manuel Giris)" -> /kiosk/checkin/
  - "QR ile Giris" -> /kiosk/qr/ (ikinci asama, simdilik placeholder)
- Alt bilgi: "Lutfen TC kimlik numaranizi hazir bulundurunuz."

### 2. templates/kiosk/checkin.html — Manuel Check-in Formu
- Form alanlari:
  - TC Kimlik No (input, maxlength=11, numeric only, buyuk font)
  - Ad Soyad (input, buyuk font)
  - Poliklinik Secimi (select/dropdown, buyuk font)
  - Doktor Secimi (select, opsiyonel, "Otomatik Atama" secenegi olsun)
- Buton: "Sira Numarasi Al"
- Validasyon (JS ile anlik):
  - TC 11 hane degilse buton disabled + kirmizi uyari.
  - Alanlar bossa uyari.
- Submit: POST /api/checkin/ (fetch API, JSON).
- Basarili yanit: /kiosk/success/?token=<uuid> sayfasina yonlendir.

### 3. templates/kiosk/success.html — Sira Basarili Ekrani
- Buyuk gosterim: "Sira Numaraniz: 24"
- Poliklinik: Dahiliye
- Doktor: Dr. Ayse Demir (varsa)
- Oda: 205 (varsa)
- Butonlar:
  - "Siram Takip Et" -> /kiosk/queue/<token>/
  - "Anamnez Doldur" -> /kiosk/anamnez/<token>/

### 4. templates/kiosk/queue.html — Hasta Sira Takip Ekrani
- URL: /kiosk/queue/<uuid:token>/ (views'de token parametre olarak alinacak)
- Gosterim:
  - Sira Numaraniz: 24 (cok buyuk font)
  - Onunuzdeki Kisi: 5 (buyuk font, kirmizi/sari/yesil renk kodlu)
  - Durum: Bekliyor / Cagrildi / Tamamlandi
  - Poliklinik: Dahiliye
  - Doktor: Dr. Ayse Demir
  - Oda: 205
- **Polling**: JavaScript `setInterval` ile her 5 saniyede bir `GET /api/queue/<token>/` cagrisi.
- Durum "called" olunca:
  - Ekran yesil arka plana donsun.
  - Buyuk "SIRANIZ GELDI" mesaji + sesli uyari (browser notification veya basit beep).
  - "Lutfen Oda 205'e geciniz."
- TC asla bu ekranda gosterilmez.

### 5. templates/kiosk/anamnez.html — AI Anamnez Sohbet Ekrani
- URL: /kiosk/anamnez/<uuid:token>/
- Chat UI (WhatsApp/Web tarzi):
  - Asistan mesajlari solda (gri balon)
  - Kullanici mesajlari sagda (mavi balon)
- Input alani + "Gonder" butonu (buyuk, dokunmatik uyumlu).
- Ilk yuklemede: POST /api/anamnez/start/ cagrisi, gelen soru gosterilir.
- Her mesaj: POST /api/anamnez/message/ cagrisi.
- Eger `risk_detected: true` donerse:
  - Kirmizi banner: "Belirttiginiz sikayetler acil degerlendirme gerektirebilir. Lutfen en yakin saglik personeline basvurunuz."
- "Bitir" butonu: POST /api/anamnez/finish/ cagrisi.
- Bitirince: Ozet gosterilir + "Doktor paneline iletildi." mesaji.

## Statik Dosyalar
- `static/css/kiosk.css`: Kiosk ozel stiller (buyuk font, butonlar, renk kodlari).
- `static/js/kiosk.js`: Check-in validasyonu, polling mantigi, anamnez chat mantigi.

## URL Yapisi (core/views.py veya ayri views)
- `/` -> Kiosk ana ekran
- `/kiosk/checkin/` -> Manuel giris formu
- `/kiosk/success/` -> Basarili ekran (query param token)
- `/kiosk/queue/<token>/` -> Sira takip
- `/kiosk/anamnez/<token>/` -> Anamnez ekrani

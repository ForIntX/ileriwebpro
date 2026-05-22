# PROMPT 07: Gelistirme Sirasi ve MVP Kontrol Listesi

## Adim Adim Implementasyon Sirasi

### Faz 1: Temel Altyapi
1. Django projesi olustur (`django-admin startproject config .`)
2. `core` ve `anamnez` app'lerini olustur
3. `requirements.txt` yaz
4. Modelleri implemente et (Prompt 01)
5. Migration al ve uygula
6. Admin paneli ayarla
7. Seed data komutu yaz (`python manage.py seed_demo`)

### Faz 2: API Katmani
8. `api_response` helper'i yaz
9. Check-in endpoint'i (POST /api/checkin/)
10. Sira durumu endpoint'i (GET /api/queue/<token>/)
11. Hasta cagirma endpoint'i (POST /api/queue/call-next/)
12. Anamnez endpoint'leri (start, message, finish)
13. Servis katmanini yaz (QueueService, AnamnezService)
14. AI motorunu yaz (ai_engine.py, question_bank.py)

### Faz 3: Frontend
15. Kiosk ana ekran (index.html)
16. Manuel check-in formu (checkin.html)
17. Basarili ekran (success.html)
18. Sira takip ekrani (queue.html) + polling
19. Anamnez sohbet ekrani (anamnez.html)
20. Doktor paneli (doctor_dashboard.html)
21. Genel numarator ekrani (queue_display.html)

### Faz 4: UI/UX ve Test
22. CSS stillerini ayarla (kiosk.css)
23. JavaScript mantigini ayarla (kiosk.js)
24. Test senaryolarini calistir (Prompt 08)
25. Demo veri ile uctan uca test

## MVP Kontrol Listesi (Teslim Oncesi Test Edilecek)
- [ ] TC bossa hata veriyor mu?
- [ ] TC 11 hane degilse hata veriyor mu?
- [ ] Poliklinik secilmezse hata veriyor mu?
- [ ] Sira numarasi dogru artiyor mu? (Ayni gun, ayni poliklinik)
- [ ] Kalan kisi sayisi dogru hesaplaniyor mu?
- [ ] Doktor cagirinca hasta durumu "called" oluyor mu?
- [ ] Hasta ekrani polling ile guncelleniyor mu? (5 saniye)
- [ ] AI ilk soruyu soruyor mu? ("Sikayetiniz nedir?")
- [ ] AI kategori tespiti yapıyor mu? ("bas agrisi" -> headache)
- [ ] AI riskli kelimeyi yakaliyor mu? ("nefes alamiyorum" -> risk_detected=true)
- [ ] AI ozet olusturuyor mu?
- [ ] Ozet doktor panelinde gorunuyor mu?
- [ ] Hasta ID yerine UUID token kullaniliyor mu?
- [ ] TC ekranda maskeleniyor mu?
- [ ] AI tani koymuyor mu?
- [ ] AI ilac onermiyor mu?

## Sunum Akisi (Demo Senaryosu)
1. Admin panelden doktor ve poliklinikleri goster.
2. Hasta kiosk ekranindan giris yap (TC: 12345678901, Ad: Test Hasta).
3. Poliklinik sec (Dahiliye).
4. Sira numarasi al (orn: 1).
5. Hasta sira ekraninda bekleme durumunu gor.
6. Hasta anamnez ekranina gec: "Basim agriyor" yaz.
7. AI kategori tespit etsin (headache), sonraki soruyu sorsun.
8. Hasta cevap versin, anamnez bitsin.
9. Doktor panelinde hasta ve ozet gorunsun.
10. Doktor "Cagir" butonuna bassin.
11. Hasta ekraninda "SIRANIZ GELDI" mesaji gorunsun.

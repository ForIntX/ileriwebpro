# PROMPT 00: Proje Brief ve Genel Mimari

## Görev
TDD dokümanına uygun, tek Django projesi olarak çalışan Hastane Kiosk ve Numaratör Sistemini implemente et. Dış AI servisi kullanılmayacak, tamamen kural tabanlı yerel AI anamnez motoru kullanılacak.

## Teknoloji Stack (Kesinlikle Değiştirme)
- **Backend**: Django 4.2+ (tek proje, frontend/backend ayrı değil)
- **Frontend**: Django Templates + HTML + CSS + Vanilla JS
- **Database**: SQLite (geliştirme için)
- **Real-time**: Polling (5 saniye aralıkla, WebSocket YOK)
- **QR**: html5-qrcode (ikinci aşamada)
- **AI**: Yerel kural tabanlı motor (dış API yasak)
- **Admin**: Django Admin

## Proje Yapısı (Kesin)
```
hospital-kiosk-system/
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── core/
│   ├── models.py
│   ├── admin.py
│   ├── views.py
│   ├── urls.py
│   └── services.py
├── anamnez/
│   ├── models.py
│   ├── admin.py
│   ├── views.py
│   ├── urls.py
│   ├── services.py
│   ├── ai_engine.py
│   └── question_bank.py
├── templates/
│   ├── kiosk/
│   ├── panel/
│   └── anamnez/
├── static/
│   ├── css/
│   └── js/
├── manage.py
└── requirements.txt
```

## Kritik Kurallar
1. Hasta ID asla URL'de açık kullanılmayacak. Her zaman `public_token` (UUID) kullanılacak.
2. QR içine TC, ad soyad veya sağlık bilgisi yazılmayacak. Sadece geçici token taşınacak.
3. TC ekranda tam gösterilmeyecek (maskele: 123456***01).
4. AI kesinlikle tanı koymayacak, ilaç/tedavi önermeyecek.
5. AI sadece doktor için ön özet üretecek.
6. Dış AI servisine (Claude, OpenAI, Gemini) hasta bilgisi gönderilmeyecek.
7. Admin panel şifreli olacak.
8. Tüm API cevapları aynı formatta olacak:
   ```json
   {"success": true, "data": {}, "message": "..."}
   {"success": false, "error": "..."}
   ```

## MVP Öncelik (İlk Teslim)
1. Hasta manuel giriş (TC + ad soyad + poliklinik)
2. Sıra numarası oluşturma
3. Hasta sıra durumu ekranı (polling 5sn)
4. Doktor paneli (hasta listesi + çağırma)
5. Yerel AI anamnez (soru-cevap + özet)
6. AI özeti doktor panelinde görünür

QR ve gelişmiş UI ikinci aşamada.

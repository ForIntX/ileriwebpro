# PROMPT 06: Guvenlik, Validasyon ve Yasaklar

## Kesin Kurallar (Asla Ihlal Etme)

### Veri Guvenligi
1. **Hasta ID URL'de acik kullanilmayacak**. Her zaman `public_token` (UUID4) kullanilacak.
2. **QR icine TC veya saglik bilgisi konulmayacak**. Sadece gecici token.
3. **TC ekranda tam gosterilmeyecek**. Maskeleme: `12345678901` -> `123456***01`.
4. **Gercek hasta verisi kullanilmayacak** (demo/test verisi disinda).
5. **Admin panel sifreli olacak**. Guclu sifre politikasi.

### AI Guvenligi (COK ONEMLI)
1. **AI tani koymayacak**. "Migrainiz var", "Gribalsiniz" gibi ifadeler YASAK.
2. **AI ilac veya tedavi onermeyecek**. "Parolol alin", "Antibiyotik kullanin" gibi ifadeler YASAK.
3. **AI sadece doktor icin on ozet uretecek**.
4. **Dis AI servisine hasta bilgisi gonderilmeyecek**. Kesinlikle API key, network call yok.

### Validasyonlar
1. **TC Kimlik No**:
   - 11 hane.
   - Sadece rakam.
   - Bos olamaz.
   - Istege bagli: TC algoritma kontrolu (ilk 9 rakamin son 2 kontrol rakami).
2. **Ad Soyad**:
   - Bos olamaz.
   - Min 2 karakter.
3. **Poliklinik**:
   - Secilmesi zorunlu.
   - Aktif polikliniklerden secilebilir.
4. **Doktor**:
   - Opsiyonel.
   - Secilirse aktif doktor olmali.

### API Guvenligi
- `@csrf_exempt` kullanilabilir (kiosk cihazlari icin).
- Rate limiting opsiyonel (simdilik gerekmez).
- Tum hatalar generic mesaj donebilir ama log'ta detayli olmali.

### Model Guvenligi
- `public_token` `editable=False`, `unique=True`.
- `anamnez_summary` sadece doktor panelinde goruntulenecek.
- `messages` JSONField icindeki hasta cevaplari sadece yetkili kullanicilarca erisilebilir.

## Hata Mesajlari (Turkce)
- "TC kimlik numarasi 11 hane olmalidir."
- "Lutfen ad soyad giriniz."
- "Lutfen poliklinik seciniz."
- "Bekleyen hasta bulunmamaktadir."
- "Gecersiz sira token'i."

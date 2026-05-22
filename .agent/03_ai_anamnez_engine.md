# PROMPT 03: Yerel AI Anamnez Motoru

## Kural 1: KESINLIKLE dis AI servisi kullanilmayacak.
- Claude, OpenAI, Gemini API cagrisi YASAK.
- Tamamen Python dictionary ve string matching ile calisacak.

## Dosyalar

### anamnez/question_bank.py
```python
QUESTION_BANK = {
    "general": [
        "Sikayetiniz nedir?",
        "Bu sikayet ne zamandir devam ediyor?",
        "Sikayetinizin siddetini 1 ile 10 arasinda puanlar misiniz?",
        "Ek bir belirtiniz var mi?",
        "Duzenli kullandiginiz ilac veya alerjiniz var mi?"
    ],
    "headache": [
        "Bas agriniz basininizin hangi bolgesinde?",
        "Bas donmesi veya gorme bulanikligi var mi?"
    ],
    "stomach": [
        "Karin agriniz tam olarak nerede?",
        "Bulanti, kusma veya ishal var mi?"
    ],
    "fever": [
        "Atesiniz kac derece olculdu?",
        "Titreme veya halsizlik var mi?"
    ],
    "chest": [
        "Gogus agriniz ne zamandir var?",
        "Nefes darligi yasiyor musunuz?"
    ]
}

SYMPTOM_KEYWORDS = {
    "headache": ["bas agrisi", "basim agriyor", "migren", "bas donmesi"],
    "stomach": ["karin agrisi", "mide", "bulanti", "kusma", "ishal"],
    "fever": ["ates", "titreme", "halsizlik", "bogaz agrisi"],
    "chest": ["gogus agrisi", "nefes darligi", "carpinti"]
}

RISK_KEYWORDS = [
    "nefes alamiyorum",
    "gogus agrisi",
    "bayildim",
    "siddetli kanama",
    "bilinc kaybi"
]
```

### anamnez/ai_engine.py
Implemente et:

```python
def detect_category(text):
    text = text.lower()
    for category, keywords in SYMPTOM_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return category
    return "general"

def check_risk(text):
    text = text.lower()
    for keyword in RISK_KEYWORDS:
        if keyword in text:
            return True
    return False

def get_next_question(category, asked_count=0):
    questions = QUESTION_BANK.get(category, QUESTION_BANK['general'])
    if asked_count < len(questions):
        return questions[asked_count]
    general_questions = QUESTION_BANK['general']
    general_index = asked_count - len(questions)
    if general_index < len(general_questions):
        return general_questions[general_index]
    return "Baska eklemek istediginiz bir sey var mi?"

def generate_summary(messages, category):
    category_display = {
        'headache': 'bas agrisi',
        'stomach': 'karin/mide sikayeti',
        'fever': 'atesli hastalik',
        'chest': 'gogus sikayeti',
        'general': 'genel sikayet'
    }
    lines = [f"Hastanin ana sikayeti kategorisi: {category_display.get(category, category)}."]
    for msg in messages:
        if msg.get('role') == 'user':
            content = msg.get('content', '')
            lines.append(f"- Hasta cevabi: {content}")
    return " ".join(lines)
```

## AI Davranis Kurallari
1. Ilk soru her zaman: "Sikayetiniz nedir?" (general[0])
2. Kategori tespit edildikten sonra o kategorinin sorularina gec.
3. Kategori sorulari bittikten sonra general sorularina devam et.
4. Risk tespit edilirse:
   - `risk_detected = True` kaydet.
   - Kullaniciya ek uyarimesaji goster (frontend'de): "Belirttiginiz sikayetler acil degerlendirme gerektirebilir. Lutfen en yakin saglik personeline basvurunuz."
   - BU BIR TANI DEGILDIR, sadece guvenlik amaclidir.
5. AI asla sunlari yapmaz:
   - Tani koymaz ("migrainiz var", "gribalsiniz" gibi).
   - Ilac onermez ("parolol alin", "antibiyotik kullanin" gibi).
   - Tedavi plani onermez.
   - Sadece sikayetleri kategorize eder ve doktora ozet sunar.

## AnamnezRecord Yapisi
`messages` JSONField formati:
```json
[
  {"role": "assistant", "content": "Sikayetiniz nedir?"},
  {"role": "user", "content": "Basim agriyor."},
  {"role": "assistant", "content": "Bas agriniz basininizin hangi bolgesinde?"},
  {"role": "user", "content": "Sakaklarimda."}
]
```

"""
anamnez/ai_engine.py

Yerel, kural tabanlı AI anamnez motoru.
KURAL: Dış AI servisi (Claude, OpenAI, Gemini vb.) KULLANILMAZ.
       Tamamen Python sözlük + string eşleşmesiyle çalışır.
       Bu motor asla tanı koymaz, ilaç önermez, tedavi planı yapmaz.
"""

from .question_bank import QUESTION_BANK, SYMPTOM_KEYWORDS, RISK_KEYWORDS


def detect_category(text: str) -> str:
    """
    Kullanıcı metnini analiz eder ve bir semptom kategorisi döndürür.
    Eşleşme yoksa 'general' döndürür.
    """
    text = text.lower()
    for category, keywords in SYMPTOM_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return category
    return "general"


def check_risk(text: str) -> bool:
    """
    Metinde acil risk anahtar kelimeleri var mı kontrol eder.
    Risk varsa True döndürür.
    NOT: Bu bir tanı değildir; yalnızca güvenlik amacıyla kullanılır.
    """
    text = text.lower()
    for keyword in RISK_KEYWORDS:
        if keyword in text:
            return True
    return False


def get_next_question(category: str, asked_count: int = 0) -> str:
    """
    Kategoriye ve şimdiye kadar sorulan soru sayısına göre bir sonraki soruyu döndürür.
    Sıra: önce kategoriye özgü sorular, ardından genel sorular.
    """
    questions = QUESTION_BANK.get(category, QUESTION_BANK['general'])
    if asked_count < len(questions):
        return questions[asked_count]
    general_questions = QUESTION_BANK['general']
    general_index = asked_count - len(questions)
    if general_index < len(general_questions):
        return general_questions[general_index]
    return "Başka eklemek istediğiniz bir şey var mı?"


def generate_summary(messages: list, category: str) -> str:
    """
    Tüm konuşma mesajlarından doktor için okunabilir bir ön özet üretir.
    UYARI: Bu özet bir tanı veya tedavi önerisi değildir.
    """
    category_display = {
        'headache': 'baş ağrısı',
        'stomach': 'karın/mide şikâyeti',
        'fever': 'ateşli hastalık',
        'chest': 'göğüs şikâyeti',
        'general': 'genel şikâyet',
    }

    lines = [
        f"Hastanın ana şikâyeti kategorisi: {category_display.get(category, category)}."
    ]
    for msg in messages:
        if msg.get('role') == 'user':
            content = msg.get('content', '')
            lines.append(f"- Hasta cevabı: {content}")

    return " ".join(lines)

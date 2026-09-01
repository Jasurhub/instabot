import re
from typing import Optional, Tuple


def validate_full_name(text: Optional[str]) -> Tuple[bool, str]:
    """
    Ism va familiyani qat'iy tekshiruvdan o'tkazish.
    
    Qoidalar:
    - Bo'sh bo'lmasligi kerak
    - Kamida 2 ta so'zdan iborat bo'lishi kerak (Ism va Familiya)
    - Ko'pi bilan 4 ta so'z (Ism, Familiya, Sharif)
    - Raqamlar, havolalar, smayliklar yoki begona belgilar bo'lmasligi kerak
    - O'zbek lotin (o', g', sh, ch, ') va kirill harflariga ruxsat beriladi
    """
    if not text or not isinstance(text, str):
        return False, "Iltimos, ism va familiyangizni matn ko'rinishida yozing."

    cleaned_text = text.strip()
    
    # Har bir so'z uzunligi va umumiy uzunlikni tekshirish
    if len(cleaned_text) < 4:
        return False, "Ism va familiya juda qisqa. Iltimos, to'liq yozing (masalan: Jasur Xolboyev)."

    if len(cleaned_text) > 80:
        return False, "Ism va familiya juda uzun. Iltimos, qisqaroq kiriting."

    # Havola (link/url) yoki maxsus belgilarni tekshirish
    if re.search(r"(http|https|t\.me|www\.|@)", cleaned_text, re.IGNORECASE):
        return False, "Ism va familiyada havolalar yoki belgilardan foydalanish mumkin emas."

    if re.search(r"\d", cleaned_text):
        return False, "Ism va familiyada raqamlar bo'lishi mumkin emas."

    # Ruxsat etilgan belgilar: Lotin, Kirill harflari, probel, defis, apostroflar (', ’, ʻ, ʼ, `)
    pattern = r"^[a-zA-Zа-яА-ЯёЁўЎғҒқҚҳҲ'\’\ʻ\ʼ\`\-\s]+$"
    if not re.match(pattern, cleaned_text):
        return False, "Ism va familiyada faqat harflardan foydalaning (masalan: Jasur Xolboyev)."

    # So'zlar sonini tekshirish
    words = [w for w in re.split(r"[\s]+", cleaned_text) if len(w) > 1]
    if len(words) < 2:
        return False, "Iltimos, ham ismingizni, ham familiyangizni kiriting (masalan: Jasur Xolboyev)."

    if len(words) > 4:
        return False, "Faqat ism va familiyangizni (zarur bo'lsa sharifingizni) kiriting."

    # Formatlash: Har bir so'z bosh harf bilan
    formatted_name = " ".join(w.capitalize() for w in words)
    return True, formatted_name


def validate_phone_number(text: Optional[str]) -> Tuple[bool, str]:
    """
    Telefon raqamini tekshirish va tozalash.
    
    Qabul qilinadigan formatlar:
    +998901234567, 998901234567, 901234567, +998 90 123 45 67
    """
    if not text or not isinstance(text, str):
        return False, "Telefon raqam noto'g'ri."

    # Bo'sh joylar, qavslar, defislar va plyusni tozalash
    raw_digits = re.sub(r"[^\d+]", "", text.strip())
    digits_only = re.sub(r"[^\d]", "", raw_digits)

    # O'zbekiston raqamlari uchun (9 ta raqam: 901234567)
    if len(digits_only) == 9 and digits_only.startswith(("9", "8", "7", "3", "5")):
        return True, f"+998{digits_only}"

    # 12 ta raqam (998901234567)
    if len(digits_only) == 12 and digits_only.startswith("998"):
        return True, f"+{digits_only}"

    # Boshqa xalqaro raqamlar (kamida 10, ko'pi bilan 15 ta raqam)
    if 10 <= len(digits_only) <= 15:
        return True, f"+{digits_only}" if not raw_digits.startswith("+") else raw_digits

    return False, "Telefon raqam formati noto'g'ri. Masalan: +998901234567 yoki pastdagi tugmani bosing."

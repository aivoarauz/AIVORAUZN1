def fmt_price(amount: int) -> str:
    """1234567 -> '1 234 567' ko'rinishida chiroyli formatlaydi."""
    return f"{amount:,}".replace(",", " ")


def split_text(text: str, limit: int = 4000):
    """Telegram xabar uzunligi cheklovi (4096) uchun uzun matnni bo'laklarga bo'ladi."""
    parts = []
    while len(text) > limit:
        idx = text.rfind("\n", 0, limit)
        if idx == -1:
            idx = limit
        parts.append(text[:idx])
        text = text[idx:]
    if text:
        parts.append(text)
    return parts

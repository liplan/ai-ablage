"""Simple document classifier based on keywords."""


def classify_document(text: str) -> str:
    lowered = text.lower()
    if "rechnung" in lowered:
        return "Rechnung"
    if "bescheid" in lowered:
        return "Bescheid"
    if "k\xc3\xbcndigung" in lowered or "kündigung" in lowered:
        return "K\u00fcndigung"
    return "Sonstiges"

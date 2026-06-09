"""Utility helpers: number-to-words (South Asian system), fiscal year."""

_ONES = [
    "", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
    "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
    "Seventeen", "Eighteen", "Nineteen",
]
_TENS = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]


def _two(n: int) -> str:
    if n < 20:
        return _ONES[n]
    return _TENS[n // 10] + (" " + _ONES[n % 10] if n % 10 else "")


def _three(n: int) -> str:
    if n < 100:
        return _two(n)
    rest = n % 100
    return _ONES[n // 100] + " Hundred" + (" " + _two(rest) if rest else "")


def number_to_words(n: int) -> str:
    """Convert integer to words using South Asian system (lakh/crore)."""
    if n == 0:
        return "Zero"
    if n < 0:
        return "Minus " + number_to_words(-n)
    parts = []
    if n >= 10_000_000:
        parts.append(_three(n // 10_000_000) + " Crore")
        n %= 10_000_000
    if n >= 100_000:
        parts.append(_two(n // 100_000) + " Lakh")
        n %= 100_000
    if n >= 1_000:
        parts.append(_two(n // 1_000) + " Thousand")
        n %= 1_000
    if n:
        parts.append(_three(n))
    return " ".join(parts)


def amount_to_words(amount: float) -> str:
    """Return NPR amount as English words, e.g. 'NPR Twenty Five Thousand ... Only'."""
    amount = round(float(amount), 2)
    rupees = int(amount)
    paisa = round((amount - rupees) * 100)
    text = "NPR " + number_to_words(rupees) + " Rupees"
    if paisa:
        text += " and " + number_to_words(paisa) + " Paisa"
    return text + " Only"


def current_fiscal_year() -> str:
    """Return Nepali fiscal year string, e.g. '081/82'."""
    from datetime import date
    today = date.today()
    # BS year ≈ AD year + 56/57; fiscal year starts mid-July (month 7)
    bs = today.year - 2000 + (57 if today.month >= 7 else 56)
    return f"{bs:03d}/{(bs + 1) % 100:02d}"


def next_invoice_no(model) -> str:
    """Generate next sequential invoice number like TI-001-082/83."""
    fy = current_fiscal_year()
    last = (
        model.query
        .filter(model.invoice_no.like(f"TI-%-{fy}"))
        .order_by(model.id.desc())
        .first()
    )
    seq = 1
    if last:
        try:
            seq = int(last.invoice_no.split("-")[1]) + 1
        except (IndexError, ValueError):
            pass
    return f"TI-{seq:03d}-{fy}"

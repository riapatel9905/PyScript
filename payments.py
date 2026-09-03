"""
Lightweight, self-contained "payment" validation.

There is no real payment gateway wired up here (that needs a merchant
account + provider SDK/API keys, e.g. Razorpay/Stripe). This module
does the kind of client-independent validation a checkout form should
always do before it even talks to a gateway: card number checksum,
expiry, CVV shape, and UPI VPA shape. Every order is recorded with a
masked reference (last 4 digits / UPI id) only - no full card data is
ever stored.
"""
import re
from datetime import datetime


def luhn_valid(card_number: str) -> bool:
    digits = [int(d) for d in card_number if d.isdigit()]
    if len(digits) < 12:
        return False
    checksum = 0
    parity = len(digits) % 2
    for i, d in enumerate(digits):
        if i % 2 == parity:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0


def validate_card(card_number, expiry, cvv):
    """expiry expected as 'MM/YY'. Returns (ok: bool, error: str|None)."""
    card_number = (card_number or "").replace(" ", "").replace("-", "")
    if not card_number.isdigit() or not (12 <= len(card_number) <= 19):
        return False, "Card number must be 12-19 digits."
    if not luhn_valid(card_number):
        return False, "Card number failed validation (checksum mismatch)."

    m = re.match(r"^(\d{2})\s*/\s*(\d{2})$", (expiry or "").strip())
    if not m:
        return False, "Expiry must be in MM/YY format."
    month, year = int(m.group(1)), int(m.group(2))
    if month < 1 or month > 12:
        return False, "Expiry month must be between 01 and 12."
    exp_year_full = 2000 + year
    now = datetime.utcnow()
    if exp_year_full < now.year or (exp_year_full == now.year and month < now.month):
        return False, "Card has expired."

    cvv = (cvv or "").strip()
    if not cvv.isdigit() or len(cvv) not in (3, 4):
        return False, "CVV must be 3 or 4 digits."

    return True, None


UPI_RE = re.compile(r"^[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}$")


def validate_upi(upi_id):
    upi_id = (upi_id or "").strip()
    if not UPI_RE.match(upi_id):
        return False, "Enter a valid UPI ID, e.g. yourname@okbank."
    return True, None

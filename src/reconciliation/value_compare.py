"""Cell-level value comparison: detects exact matches, format-only
differences (e.g. date or number formatting), and true value mismatches.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional, Tuple

from dateutil import parser as date_parser

MATCH = "MATCH"
FORMAT_MISMATCH = "FORMAT_MISMATCH"
VALUE_MISMATCH = "VALUE_MISMATCH"

_DATE_FORMATS_TRIED = (
    "%d/%m/%Y",
    "%Y-%m-%d",
    "%m/%d/%Y",
    "%d-%m-%Y",
    "%d.%m.%Y",
    "%Y/%m/%d",
)


def _clean(value) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() in ("nan", "none", "nat"):
        return ""
    return text


def _try_parse_number(text: str) -> Optional[float]:
    if text == "":
        return None
    cleaned = text.replace(",", "").replace(" ", "")
    # Strip common currency symbols.
    for symbol in ("RM", "MYR", "$", "USD", "€", "£"):
        if cleaned.upper().startswith(symbol.upper()):
            cleaned = cleaned[len(symbol):]
    cleaned = cleaned.strip()
    if cleaned.endswith("%"):
        cleaned = cleaned[:-1]
    try:
        return float(cleaned)
    except ValueError:
        return None


def _try_parse_date(text: str) -> Optional[datetime]:
    if text == "" or len(text) < 6:
        return None
    for fmt in _DATE_FORMATS_TRIED:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    try:
        # dayfirst=False default; only trust dateutil if the string looks
        # date-like (contains digits and a separator) to avoid false
        # positives on plain text fields.
        if not any(sep in text for sep in ("/", "-", ".")):
            return None
        return date_parser.parse(text, fuzzy=False)
    except (ValueError, OverflowError):
        return None


def compare_values(value_1, value_2) -> Tuple[str, str, str]:
    """Compare two raw cell values.

    Returns (status, normalized_display_1, normalized_display_2) where
    status is one of MATCH, FORMAT_MISMATCH, VALUE_MISMATCH.
    """
    text_1 = _clean(value_1)
    text_2 = _clean(value_2)

    if text_1 == text_2:
        return MATCH, text_1, text_2

    if text_1 == "" or text_2 == "":
        # One side missing a value while the other has one is a real
        # value difference, not a formatting quirk.
        return VALUE_MISMATCH, text_1, text_2

    # Try numeric comparison (handles "100.00" vs "100", "1,000" vs "1000").
    num_1 = _try_parse_number(text_1)
    num_2 = _try_parse_number(text_2)
    if num_1 is not None and num_2 is not None:
        if abs(num_1 - num_2) < 1e-9:
            return FORMAT_MISMATCH, text_1, text_2
        return VALUE_MISMATCH, text_1, text_2

    # Try date comparison (handles DD/MM/YYYY vs YYYY-MM-DD, etc.).
    date_1 = _try_parse_date(text_1)
    date_2 = _try_parse_date(text_2)
    if date_1 is not None and date_2 is not None:
        if date_1.date() == date_2.date():
            return FORMAT_MISMATCH, text_1, text_2
        return VALUE_MISMATCH, text_1, text_2

    # Case/whitespace-only differences count as a format mismatch.
    if text_1.strip().lower() == text_2.strip().lower():
        return FORMAT_MISMATCH, text_1, text_2

    return VALUE_MISMATCH, text_1, text_2

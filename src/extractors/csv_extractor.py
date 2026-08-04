"""CSV extraction with delimiter and encoding sniffing."""
from __future__ import annotations

import csv
import io

import pandas as pd


def _read_bytes(uploaded_file) -> bytes:
    if hasattr(uploaded_file, "seek"):
        try:
            uploaded_file.seek(0)
        except Exception:  # noqa: BLE001
            pass
    data = uploaded_file.read()
    if hasattr(uploaded_file, "seek"):
        try:
            uploaded_file.seek(0)
        except Exception:  # noqa: BLE001
            pass
    return data


def load_csv(uploaded_file) -> pd.DataFrame:
    """Load a CSV file into a DataFrame, auto-detecting delimiter and encoding."""
    raw = _read_bytes(uploaded_file)

    text = None
    for encoding in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
        try:
            text = raw.decode(encoding)
            break
        except (UnicodeDecodeError, AttributeError):
            continue
    if text is None:
        text = raw.decode("utf-8", errors="replace")

    sample = text[:4096]
    delimiter = ","
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        delimiter = dialect.delimiter
    except csv.Error:
        pass

    df = pd.read_csv(io.StringIO(text), sep=delimiter, dtype=str, keep_default_na=False)
    df.columns = [str(c).strip() for c in df.columns]
    return df

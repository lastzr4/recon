"""PDF table extraction using pdfplumber, with pypdf as a text-layer fallback check."""
from __future__ import annotations

import io
from typing import List, TYPE_CHECKING

import pandas as pd
import pdfplumber

if TYPE_CHECKING:
    from . import TableCandidate


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


def _table_to_dataframe(raw_table: List[List[str]]) -> pd.DataFrame:
    if not raw_table or len(raw_table) < 2:
        return pd.DataFrame()
    header = [str(c).strip() if c is not None else "" for c in raw_table[0]]
    # De-duplicate blank/repeated headers so pandas doesn't choke.
    seen = {}
    clean_header = []
    for i, col in enumerate(header):
        name = col if col else f"Column_{i + 1}"
        if name in seen:
            seen[name] += 1
            name = f"{name}_{seen[name]}"
        else:
            seen[name] = 0
        clean_header.append(name)

    rows = [
        [("" if cell is None else str(cell).strip()) for cell in row]
        for row in raw_table[1:]
    ]
    df = pd.DataFrame(rows, columns=clean_header)
    # Drop fully blank rows produced by PDF layout noise.
    df = df[~(df.apply(lambda r: all(v == "" for v in r), axis=1))]
    return df.reset_index(drop=True)


def extract_pdf_tables(uploaded_file) -> List["TableCandidate"]:
    """Extract every table found across all pages of a PDF as candidates."""
    from . import TableCandidate  # local import avoids circular import

    raw = _read_bytes(uploaded_file)
    candidates: List[TableCandidate] = []

    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        for page_index, page in enumerate(pdf.pages, start=1):
            raw_tables = page.extract_tables(
                table_settings={
                    "vertical_strategy": "lines",
                    "horizontal_strategy": "lines",
                }
            )
            if not raw_tables:
                # Retry with a more lenient text-based strategy for
                # borderless tables.
                raw_tables = page.extract_tables(
                    table_settings={
                        "vertical_strategy": "text",
                        "horizontal_strategy": "text",
                    }
                )

            for table_index, raw_table in enumerate(raw_tables, start=1):
                df = _table_to_dataframe(raw_table)
                if df.empty or df.shape[1] < 1:
                    continue
                label = f"Page {page_index} - Table {table_index} ({df.shape[0]} rows x {df.shape[1]} cols)"
                candidates.append(TableCandidate(label=label, dataframe=df))

    return candidates

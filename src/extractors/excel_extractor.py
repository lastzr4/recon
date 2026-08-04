"""Excel extraction supporting multi-sheet workbooks."""
from __future__ import annotations

from typing import Dict

import pandas as pd


def load_excel_sheets(uploaded_file) -> Dict[str, pd.DataFrame]:
    """Load every non-empty sheet in an Excel workbook.

    Returns a dict mapping sheet name -> DataFrame (all cells as strings,
    blanks kept as empty strings rather than NaN, for reliable comparison).
    """
    if hasattr(uploaded_file, "seek"):
        try:
            uploaded_file.seek(0)
        except Exception:  # noqa: BLE001
            pass

    xls = pd.ExcelFile(uploaded_file)
    sheets: Dict[str, pd.DataFrame] = {}
    for name in xls.sheet_names:
        df = xls.parse(sheet_name=name, dtype=str, keep_default_na=False)
        df.columns = [str(c).strip() for c in df.columns]
        # Skip fully empty sheets (no columns or no rows) so they don't
        # clutter the sheet-selection UI.
        if df.shape[1] == 0 or df.dropna(how="all").shape[0] == 0:
            continue
        sheets[name] = df

    if not sheets:
        # Fall back to returning the first sheet even if it looked empty,
        # so the caller always has something to work with.
        first_name = xls.sheet_names[0]
        sheets[first_name] = xls.parse(sheet_name=first_name, dtype=str, keep_default_na=False)

    return sheets

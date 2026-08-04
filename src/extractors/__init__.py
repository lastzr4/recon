"""File extraction package: unified loading for CSV, Excel, and PDF sources."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

import pandas as pd

from .csv_extractor import load_csv
from .excel_extractor import load_excel_sheets
from .pdf_extractor import extract_pdf_tables


@dataclass
class TableCandidate:
    """A single candidate table extracted from a source file."""

    label: str
    dataframe: pd.DataFrame


@dataclass
class ExtractionResult:
    """Result of extracting tabular data from an uploaded file.

    kind == "single": `dataframe` is ready to use directly.
    kind == "multi": the caller must let the user pick one of `tables`.
    """

    kind: str
    filename: str
    dataframe: Optional[pd.DataFrame] = None
    tables: List[TableCandidate] = field(default_factory=list)
    error: Optional[str] = None


def extract_file(uploaded_file) -> ExtractionResult:
    """Detect file type by extension and extract tabular data.

    `uploaded_file` is expected to behave like a Streamlit UploadedFile
    (has `.name` and is readable/seekable as bytes), but any file-like
    object with a `.name` attribute works.
    """
    filename = getattr(uploaded_file, "name", "uploaded_file")
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    try:
        if ext == "csv":
            df = load_csv(uploaded_file)
            return ExtractionResult(kind="single", filename=filename, dataframe=df)

        if ext in ("xlsx", "xls"):
            sheets = load_excel_sheets(uploaded_file)
            if len(sheets) == 1:
                only_df = next(iter(sheets.values()))
                return ExtractionResult(kind="single", filename=filename, dataframe=only_df)
            candidates = [
                TableCandidate(label=f"Sheet: {name}", dataframe=df)
                for name, df in sheets.items()
            ]
            return ExtractionResult(kind="multi", filename=filename, tables=candidates)

        if ext == "pdf":
            tables = extract_pdf_tables(uploaded_file)
            if not tables:
                return ExtractionResult(
                    kind="single",
                    filename=filename,
                    error="No tables could be detected in this PDF.",
                )
            if len(tables) == 1:
                return ExtractionResult(
                    kind="single", filename=filename, dataframe=tables[0].dataframe
                )
            return ExtractionResult(kind="multi", filename=filename, tables=tables)

        return ExtractionResult(
            kind="single",
            filename=filename,
            error=f"Unsupported file type: .{ext}. Please upload .xlsx, .xls, .csv, or .pdf.",
        )
    except Exception as exc:  # noqa: BLE001 - surface extraction errors to the UI
        return ExtractionResult(kind="single", filename=filename, error=str(exc))

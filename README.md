# Data Reconciliation Tool

Production-ready Streamlit web app for comparing data between two files
(Excel, CSV, or PDF) with automatic/manual field mapping, a
color-highlighted comparison dashboard, and a downloadable multi-sheet
Excel report.

## Features

- Upload **File 1** and **File 2** in `.xlsx`, `.xls`, `.csv`, or `.pdf` format.
- PDF tables are extracted automatically with `pdfplumber`; if a PDF or
  workbook has multiple tables/sheets, you pick the correct one.
- Columns are auto-mapped (case-insensitive, whitespace-trimmed, plus
  fuzzy matching for near-identical names) with a manual override UI.
- Select one or more mapped fields as the **Primary Key** to merge records.
- The comparison engine detects both value differences and
  **format-only** differences (e.g. `31/12/2025` vs `2025-12-31`, or
  `100.00` vs `100`), and classifies every record as `MATCH`,
  `MISMATCH`, `MISSING_IN_FILE_1`, or `MISSING_IN_FILE_2`.
- Dashboard with summary metric cards, an overall `MATCH` / `XMATCH`
  badge, mapped/unmapped field breakdown, and a filterable,
  color-highlighted detail table.
- One-click export to a 3-sheet Excel report: Executive Summary,
  Detailed Mismatch Log, and Unmapped Fields Info.

## Project Structure

```
recon/
├── app.py                      # Streamlit entry point
├── requirements.txt
├── Dockerfile
├── Procfile
├── railway.json
├── .streamlit/config.toml
├── src/
│   ├── extractors/             # CSV / Excel / PDF ingestion
│   ├── mapping/                # Auto + manual field mapping
│   ├── reconciliation/         # Comparison engine + value normalization
│   ├── export/                 # Multi-sheet Excel report builder
│   └── ui/                     # Streamlit components & styling
├── tests/                      # Unit tests (pytest)
└── sample_data/                # Example CSVs for a quick demo
```

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Open the URL Streamlit prints (default `http://localhost:8501`).

## Run Tests

```bash
pip install pytest
pytest
```

## Deploy to Railway

This repo includes a `Dockerfile`, `Procfile`, and `railway.json`, so
Railway will build and run it out of the box:

1. Push this repo to GitHub.
2. In Railway, create a project from the GitHub repo (or connect an
   existing empty project's service to it).
3. Railway detects the `Dockerfile` and builds automatically. No extra
   environment variables are required — the app reads `$PORT` at runtime.
4. Once deployed, open the generated Railway domain to use the app.

## How Reconciliation Works

1. **Extract** — each file is parsed into a table (PDF tables via
   `pdfplumber`, spreadsheets via `pandas`/`openpyxl`).
2. **Map fields** — columns with matching names (case/whitespace
   insensitive) are auto-mapped; anything else can be mapped manually.
3. **Pick a primary key** — one or more mapped fields used to merge
   File 1 and File 2 records (an outer join).
4. **Compare** — for every mapped field on matched records, values are
   compared after light normalization. Numbers and dates that are
   equal but formatted differently are flagged as a *format*
   difference; everything else that differs is a *value* difference.
   Either type marks the record `MISMATCH`.
5. **Report** — results are shown on-screen and exportable as an Excel
   workbook with a summary, a detailed mismatch log, and unmapped
   field info.

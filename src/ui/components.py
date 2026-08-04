"""Reusable Streamlit rendering components for the reconciliation dashboard."""
from __future__ import annotations

from typing import List

import pandas as pd
import streamlit as st

from ..reconciliation.engine import ReconciliationResult

STATUS_COLORS = {
    "MATCH": "#ECFDF5",
    "FORMAT_MISMATCH": "#FFFBEB",
    "VALUE_MISMATCH": "#FEF2F2",
    "N/A": "#F8FAFC",
}
ROW_STATUS_STYLE = {
    "MATCH": "background-color:#ECFDF5; color:#059669; font-weight:700;",
    "MISMATCH": "background-color:#FEF2F2; color:#DC2626; font-weight:700;",
    "MISSING_IN_FILE_1": "background-color:#FFFBEB; color:#D97706; font-weight:700;",
    "MISSING_IN_FILE_2": "background-color:#FFFBEB; color:#D97706; font-weight:700;",
}
CHIP_CLASS = {
    "exact": "field-chip-exact",
    "fuzzy": "field-chip-fuzzy",
    "manual": "field-chip-manual",
}


def render_app_header() -> None:
    st.markdown(
        """
        <div class="recon-app-header">
            <div class="recon-app-mark">RT</div>
            <div>
                <div class="recon-app-title">Data Reconciliation Tool</div>
                <div class="recon-app-subtitle">Upload two files, map fields, and get an instant reconciliation report.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_step_header(number: int, title: str, desc: str = "") -> None:
    st.markdown(
        f'<div class="recon-step"><div class="recon-step-number">{number}</div>'
        f'<div class="recon-step-title">{title}</div></div>',
        unsafe_allow_html=True,
    )
    if desc:
        st.markdown(f'<div class="recon-step-desc">{desc}</div>', unsafe_allow_html=True)


def render_overall_badge(overall_status: str) -> None:
    if overall_status == "MATCH":
        html = (
            '<div class="recon-badge-wrap"><div class="recon-badge recon-badge-match">'
            '<span class="recon-badge-icon">&#10003;</span> ALL RECORDS MATCH</div></div>'
        )
    else:
        html = (
            '<div class="recon-badge-wrap"><div class="recon-badge recon-badge-xmatch">'
            '<span class="recon-badge-icon">&#10007;</span> DISCREPANCIES FOUND (XMATCH)</div></div>'
        )
    st.markdown(html, unsafe_allow_html=True)


def _card(label: str, value, accent: str) -> str:
    return (
        f'<div class="recon-card" style="--recon-accent:{accent}">'
        f'<div class="recon-card-label">{label}</div>'
        f'<div class="recon-card-value">{value}</div></div>'
    )


def render_metric_cards(summary: dict) -> None:
    neutral = "#94A3B8"
    row_1 = st.columns(4)
    cards_1 = [
        ("Records - File 1", summary["total_records_file_1"], neutral),
        ("Records - File 2", summary["total_records_file_2"], neutral),
        ("Mapped Fields", summary["mapped_fields_count"], "#4338CA"),
        ("Unmapped Fields", summary["unmapped_fields_count"], "#94A3B8"),
    ]
    for col, (label, value, accent) in zip(row_1, cards_1):
        with col:
            st.markdown(_card(label, value, accent), unsafe_allow_html=True)

    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

    row_2 = st.columns(4)
    cards_2 = [
        ("Match", summary["match_count"], "#059669"),
        ("Mismatch", summary["mismatch_count"], "#DC2626"),
        ("Missing - File 1", summary["missing_in_file_1_count"], "#D97706"),
        ("Missing - File 2", summary["missing_in_file_2_count"], "#D97706"),
    ]
    for col, (label, value, accent) in zip(row_2, cards_2):
        with col:
            st.markdown(_card(label, value, accent), unsafe_allow_html=True)

    st.markdown(
        f"<div style='margin-top:0.9rem; font-size:0.85rem; color:#64748B;'>"
        f"Match rate: <strong style='color:#0F172A'>{summary['match_rate_percent']}%</strong> across "
        f"{summary['total_compared_records']} compared records.</div>",
        unsafe_allow_html=True,
    )
    if summary.get("duplicate_keys_file_1") or summary.get("duplicate_keys_file_2"):
        st.warning(
            f"Duplicate primary keys detected and only the first occurrence was kept: "
            f"{summary['duplicate_keys_file_1']} in File 1, {summary['duplicate_keys_file_2']} in File 2."
        )


def render_mapping_breakdown(result: ReconciliationResult) -> None:
    left, right = st.columns([3, 2])

    with left:
        st.markdown("**Mapped Fields**")
        if result.mapped_fields:
            pk_labels = set(result.primary_key_labels)
            rows_html = []
            for m in result.mapped_fields:
                label = m.field_1 if m.field_1 == m.field_2 else f"{m.field_1} / {m.field_2}"
                chip_class = CHIP_CLASS.get(m.match_type, "field-chip-manual")
                pk_tag = " &nbsp;<span class='field-chip field-chip-manual' style='background:#0F172A22;color:#0F172A;'>PK</span>" if label in pk_labels else ""
                rows_html.append(
                    "<div class='recon-map-row'>"
                    f"<span class='recon-map-field'>{m.field_1}</span>"
                    f"<span class='recon-map-arrow'>&#8594;</span>"
                    f"<span class='recon-map-field'>{m.field_2}</span>"
                    f"&nbsp;&nbsp;<span class='field-chip {chip_class}'>{m.match_type}</span>{pk_tag}"
                    "</div>"
                )
            st.markdown("".join(rows_html), unsafe_allow_html=True)
        else:
            st.info("No fields mapped yet.")

    with right:
        st.markdown("**Unmapped Fields**")
        u1, u2 = result.unmapped_file_1, result.unmapped_file_2
        if not u1 and not u2:
            st.success("All fields are mapped between both files.")
        else:
            if u1:
                chips = "".join(f"<span class='field-chip field-chip-unmapped'>{f}</span> " for f in u1)
                st.markdown(f"<div style='margin-bottom:0.4rem;'><span style='font-size:0.78rem;color:#64748B;'>File 1 only:</span><br>{chips}</div>", unsafe_allow_html=True)
            if u2:
                chips = "".join(f"<span class='field-chip field-chip-unmapped'>{f}</span> " for f in u2)
                st.markdown(f"<div><span style='font-size:0.78rem;color:#64748B;'>File 2 only:</span><br>{chips}</div>", unsafe_allow_html=True)


def build_styled_table(detail_df: pd.DataFrame, field_labels: List[str]):
    """Build a display DataFrame plus a Styler with per-cell diff highlighting."""
    df = detail_df.reset_index(drop=True)

    display_cols = ["Primary Key"]
    rename_map = {}
    for label in field_labels:
        c1, c2 = f"{label}::File1", f"{label}::File2"
        display_cols.extend([c1, c2])
        rename_map[c1] = f"{label} (File 1)"
        rename_map[c2] = f"{label} (File 2)"
    display_cols.append("Row_Status")
    rename_map["Row_Status"] = "Row Status"

    display_df = df[display_cols].rename(columns=rename_map)

    reverse_col_map = {v: k for k, v in rename_map.items()}

    def _highlight_row(row: pd.Series) -> List[str]:
        idx = row.name
        src = df.loc[idx]
        styles = []
        for col in display_df.columns:
            if col == "Primary Key":
                styles.append("")
            elif col == "Row Status":
                styles.append(ROW_STATUS_STYLE.get(src["Row_Status"], ""))
            else:
                original_col = reverse_col_map[col]
                label = original_col.rsplit("::", 1)[0]
                cell_status = src.get(f"{label}::Status", "")
                color = STATUS_COLORS.get(cell_status, "")
                styles.append(f"background-color:{color};" if color else "")
        return styles

    styler = display_df.style.apply(_highlight_row, axis=1)
    return display_df, styler

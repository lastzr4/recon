"""Reusable Streamlit rendering components for the reconciliation dashboard."""
from __future__ import annotations

from typing import List

import pandas as pd
import streamlit as st

from ..reconciliation.engine import ReconciliationResult

STATUS_COLORS = {
    "MATCH": "#E2F0D9",
    "FORMAT_MISMATCH": "#FFEB9C",
    "VALUE_MISMATCH": "#FFC7CE",
    "N/A": "#F1F1F1",
}
ROW_STATUS_STYLE = {
    "MATCH": "background-color:#C6EFCE; color:#0B6B0B; font-weight:700;",
    "MISMATCH": "background-color:#FFC7CE; color:#9C0006; font-weight:700;",
    "MISSING_IN_FILE_1": "background-color:#FFE0B2; color:#7A4A00; font-weight:700;",
    "MISSING_IN_FILE_2": "background-color:#FFE0B2; color:#7A4A00; font-weight:700;",
}


def render_overall_badge(overall_status: str) -> None:
    if overall_status == "MATCH":
        st.markdown('<div class="recon-badge recon-badge-match">MATCH</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="recon-badge recon-badge-xmatch">XMATCH</div>', unsafe_allow_html=True)


def render_metric_cards(summary: dict) -> None:
    row_1 = st.columns(4)
    cards_1 = [
        ("Total Records - File 1", summary["total_records_file_1"]),
        ("Total Records - File 2", summary["total_records_file_2"]),
        ("Mapped Fields", summary["mapped_fields_count"]),
        ("Unmapped Fields", summary["unmapped_fields_count"]),
    ]
    for col, (label, value) in zip(row_1, cards_1):
        with col:
            st.markdown(
                f'<div class="recon-card"><div class="recon-card-label">{label}</div>'
                f'<div class="recon-card-value">{value}</div></div>',
                unsafe_allow_html=True,
            )

    row_2 = st.columns(4)
    cards_2 = [
        ("MATCH Records", summary["match_count"]),
        ("MISMATCH Records", summary["mismatch_count"]),
        ("Missing in File 1", summary["missing_in_file_1_count"]),
        ("Missing in File 2", summary["missing_in_file_2_count"]),
    ]
    for col, (label, value) in zip(row_2, cards_2):
        with col:
            st.markdown(
                f'<div class="recon-card"><div class="recon-card-label">{label}</div>'
                f'<div class="recon-card-value">{value}</div></div>',
                unsafe_allow_html=True,
            )

    st.caption(
        f"Match rate: **{summary['match_rate_percent']}%** across "
        f"{summary['total_compared_records']} compared records."
    )
    if summary.get("duplicate_keys_file_1") or summary.get("duplicate_keys_file_2"):
        st.warning(
            f"Duplicate primary keys detected and only the first occurrence was kept: "
            f"{summary['duplicate_keys_file_1']} in File 1, {summary['duplicate_keys_file_2']} in File 2."
        )


def render_mapping_breakdown(result: ReconciliationResult) -> None:
    left, right = st.columns(2)

    with left:
        st.markdown("**Mapped Fields**")
        if result.mapped_fields:
            rows = []
            pk_labels = set(result.primary_key_labels)
            for m in result.mapped_fields:
                label = m.field_1 if m.field_1 == m.field_2 else f"{m.field_1} / {m.field_2}"
                rows.append(
                    {
                        "File 1 Field": m.field_1,
                        "File 2 Field": m.field_2,
                        "Match Type": m.match_type,
                        "Primary Key": "Yes" if label in pk_labels else "",
                    }
                )
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("No fields mapped yet.")

    with right:
        st.markdown("**Unmapped Fields**")
        u1, u2 = result.unmapped_file_1, result.unmapped_file_2
        if not u1 and not u2:
            st.success("All fields are mapped between both files.")
        else:
            if u1:
                st.caption("File 1 only:")
                st.write(", ".join(u1))
            if u2:
                st.caption("File 2 only:")
                st.write(", ".join(u2))


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

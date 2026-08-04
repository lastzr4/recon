"""Data Reconciliation Tool - Streamlit entry point.

Upload two files (Excel/CSV/PDF), map their fields, pick a primary key,
run the reconciliation engine, and export a multi-sheet Excel report.
"""
from __future__ import annotations

import io

import pandas as pd
import streamlit as st

from src.export.excel_exporter import export_to_excel
from src.extractors import ExtractionResult, extract_file
from src.mapping.field_mapper import FieldMapping, auto_map_columns
from src.reconciliation.engine import reconcile
from src.ui.components import (
    build_styled_table,
    render_app_header,
    render_mapping_breakdown,
    render_metric_cards,
    render_overall_badge,
    render_step_header,
)
from src.ui.styles import CUSTOM_CSS

st.set_page_config(
    page_title="Data Reconciliation Tool",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


class _InMemoryFile(io.BytesIO):
    """Lightweight file-like wrapper so extraction functions can be cached
    on plain bytes rather than an UploadedFile object.

    Subclasses io.BytesIO (rather than hand-rolling read/seek) so it also
    supports .tell() and correct partial-read semantics, both of which
    pandas.ExcelFile/openpyxl rely on internally when parsing .xlsx files.
    """

    def __init__(self, data: bytes, name: str):
        super().__init__(data)
        self.name = name


@st.cache_data(show_spinner=False)
def _extract_cached(file_bytes: bytes, filename: str) -> ExtractionResult:
    return extract_file(_InMemoryFile(file_bytes, filename))


def _field_label(field_1: str, field_2: str) -> str:
    return field_1 if field_1 == field_2 else f"{field_1} / {field_2}"


def _upload_and_select(slot: str, label: str):
    """Render an upload widget for one file slot and return the resolved
    DataFrame (or None if not ready) plus the display filename."""
    st.markdown(f"<div style='font-weight:700; font-size:0.92rem; margin-bottom:0.35rem;'>{label}</div>", unsafe_allow_html=True)
    uploaded = st.file_uploader(
        label, type=["xlsx", "xls", "csv", "pdf"], key=f"uploader_{slot}", label_visibility="collapsed"
    )
    if uploaded is None:
        return None, None

    result = _extract_cached(uploaded.getvalue(), uploaded.name)

    if result.error:
        st.error(f"{label}: {result.error}")
        return None, uploaded.name

    if result.kind == "multi":
        options = [t.label for t in result.tables]
        choice = st.selectbox(
            f"Multiple tables found in {uploaded.name} - select the correct one:",
            options,
            key=f"table_choice_{slot}",
        )
        chosen = next(t for t in result.tables if t.label == choice)
        df = chosen.dataframe
    else:
        df = result.dataframe

    if df is None or df.empty:
        st.warning(f"{label}: no usable rows were found.")
        return None, uploaded.name

    st.caption(f"✓ {uploaded.name} — {df.shape[0]} rows × {df.shape[1]} cols")
    with st.expander("Preview"):
        st.dataframe(df.head(10), use_container_width=True, hide_index=True)

    return df, uploaded.name


def main() -> None:
    render_app_header()

    render_step_header(1, "Upload Files")
    with st.container(border=True):
        col_1, col_2 = st.columns(2)
        with col_1:
            df_1, name_1 = _upload_and_select("1", "File 1")
        with col_2:
            df_2, name_2 = _upload_and_select("2", "File 2")

    if df_1 is None or df_2 is None:
        st.info("Upload both files to continue.")
        return

    df_1 = df_1.copy()
    df_2 = df_2.copy()
    df_1.columns = [str(c).strip() for c in df_1.columns]
    df_2.columns = [str(c).strip() for c in df_2.columns]
    cols_1 = list(df_1.columns)
    cols_2 = list(df_2.columns)

    render_step_header(
        2,
        "Field Mapping",
        "Fields with identical names are auto-mapped. Adjust any dropdown to map fields with different names (e.g. “Invoice No” to “Inv_Num”).",
    )

    auto_mappings, _, _ = auto_map_columns(cols_1, cols_2)
    auto_map_dict = {m.field_1: m.field_2 for m in auto_mappings}
    auto_type_dict = {m.field_1: m.match_type for m in auto_mappings}

    not_mapped_option = "-- Not Mapped --"
    selections: dict[str, str] = {}

    with st.container(border=True):
        map_col_1, map_col_2, map_col_3 = st.columns([2, 2, 1])
        with map_col_1:
            st.markdown("<span style='font-size:0.78rem;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:0.03em;'>File 1 Field</span>", unsafe_allow_html=True)
        with map_col_2:
            st.markdown("<span style='font-size:0.78rem;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:0.03em;'>Maps to File 2 Field</span>", unsafe_allow_html=True)
        with map_col_3:
            st.markdown("<span style='font-size:0.78rem;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:0.03em;'>Match</span>", unsafe_allow_html=True)

        st.markdown("<hr style='margin:0.5rem 0;'>", unsafe_allow_html=True)

        for c1 in cols_1:
            row_1, row_2, row_3 = st.columns([2, 2, 1], vertical_alignment="center")
            options = [not_mapped_option] + cols_2
            default_value = auto_map_dict.get(c1, not_mapped_option)
            default_index = options.index(default_value) if default_value in options else 0
            with row_1:
                st.markdown(f"<span style='font-weight:600; font-size:0.9rem;'>{c1}</span>", unsafe_allow_html=True)
            with row_2:
                choice = st.selectbox(
                    c1, options, index=default_index, key=f"map_select_{c1}", label_visibility="collapsed"
                )
                selections[c1] = choice
            with row_3:
                if choice == not_mapped_option:
                    st.markdown("<span class='field-chip field-chip-unmapped'>unmapped</span>", unsafe_allow_html=True)
                elif choice == auto_map_dict.get(c1):
                    mtype = auto_type_dict.get(c1, "manual")
                    st.markdown(f"<span class='field-chip field-chip-{mtype}'>{mtype}</span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span class='field-chip field-chip-manual'>manual</span>", unsafe_allow_html=True)

    chosen_targets = [v for v in selections.values() if v != not_mapped_option]
    duplicate_targets = sorted({v for v in chosen_targets if chosen_targets.count(v) > 1})
    if duplicate_targets:
        st.error(
            "Each File 2 field can only be mapped once. Fix duplicate mapping(s) for: "
            + ", ".join(duplicate_targets)
        )
        return

    mapped_fields = [
        FieldMapping(
            field_1=c1,
            field_2=c2,
            match_type=(
                auto_type_dict.get(c1, "manual") if auto_map_dict.get(c1) == c2 else "manual"
            ),
        )
        for c1, c2 in selections.items()
        if c2 != not_mapped_option
    ]
    unmapped_1 = [c1 for c1 in cols_1 if selections.get(c1) == not_mapped_option]
    unmapped_2 = [c2 for c2 in cols_2 if c2 not in chosen_targets]

    if not mapped_fields:
        st.warning("Map at least one field pair to continue.")
        return

    render_step_header(3, "Primary Key Selection", "Choose at least one mapped field to uniquely identify and merge records.")
    with st.container(border=True):
        field_options = [_field_label(m.field_1, m.field_2) for m in mapped_fields]
        pk_selection = st.multiselect("Primary Key field(s)", field_options, key="pk_selection", label_visibility="collapsed", placeholder="Choose one or more fields")

    if not pk_selection:
        st.info("Select at least one primary key field to run the reconciliation.")
        return

    primary_keys = [m for m in mapped_fields if _field_label(m.field_1, m.field_2) in pk_selection]

    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
    _, btn_col, _ = st.columns([1, 1, 1])
    with btn_col:
        run = st.button("Run Reconciliation", type="primary", use_container_width=True)

    if run:
        with st.spinner("Reconciling records..."):
            try:
                result = reconcile(df_1, df_2, mapped_fields, primary_keys, unmapped_1, unmapped_2)
            except Exception as exc:  # noqa: BLE001
                st.error(f"Reconciliation failed: {exc}")
                return
        st.session_state["recon_result"] = result
        st.session_state["recon_file_names"] = (name_1, name_2)

    result = st.session_state.get("recon_result")
    if result is None:
        return

    render_step_header(4, "Reconciliation Dashboard")
    with st.container(border=True):
        render_overall_badge(result.summary["overall_status"])
        render_metric_cards(result.summary)

    st.markdown("<div style='height:0.9rem'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("<div style='font-weight:700; font-size:0.95rem; margin-bottom:0.6rem;'>Field Mapping Breakdown</div>", unsafe_allow_html=True)
        render_mapping_breakdown(result)

    st.markdown("<div style='height:0.9rem'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("<div style='font-weight:700; font-size:0.95rem; margin-bottom:0.6rem;'>Detailed Comparison</div>", unsafe_allow_html=True)
        filter_choice = st.radio(
            "Filter",
            ["All", "Match Only", "Mismatch Only", "Missing Only"],
            horizontal=True,
            key="detail_filter",
            label_visibility="collapsed",
        )
        detail_df = result.detail_df
        if filter_choice == "Match Only":
            view_df = detail_df[detail_df["Row_Status"] == "MATCH"]
        elif filter_choice == "Mismatch Only":
            view_df = detail_df[detail_df["Row_Status"] == "MISMATCH"]
        elif filter_choice == "Missing Only":
            view_df = detail_df[
                detail_df["Row_Status"].isin(["MISSING_IN_FILE_1", "MISSING_IN_FILE_2"])
            ]
        else:
            view_df = detail_df

        st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
        if view_df.empty:
            st.info("No records match this filter.")
        else:
            display_df, styler = build_styled_table(view_df, result.field_labels)
            st.dataframe(styler, use_container_width=True, hide_index=True)
            st.caption(f"Showing {len(display_df)} of {len(detail_df)} records.")

    st.markdown("<div style='height:0.9rem'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        exp_col_1, exp_col_2 = st.columns([3, 1], vertical_alignment="center")
        with exp_col_1:
            st.markdown(
                "<div style='font-weight:700; font-size:0.95rem;'>Export Report</div>"
                "<div style='font-size:0.82rem; color:#64748B; margin-top:0.15rem;'>"
                "Excel workbook with Executive Summary, Detailed Mismatch Log, and Unmapped Fields Info.</div>",
                unsafe_allow_html=True,
            )
        with exp_col_2:
            file_names = st.session_state.get("recon_file_names", ("File 1", "File 2"))
            excel_bytes = export_to_excel(result, file_names[0], file_names[1])
            st.download_button(
                "Download .xlsx",
                data=excel_bytes,
                file_name="reconciliation_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )


if __name__ == "__main__":
    main()

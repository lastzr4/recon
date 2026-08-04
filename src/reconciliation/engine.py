"""Core reconciliation engine: merges two datasets on a primary key and
compares every mapped field, classifying each record and cell.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import pandas as pd

from ..mapping.field_mapper import FieldMapping
from .value_compare import MATCH, compare_values

ROW_MATCH = "MATCH"
ROW_MISMATCH = "MISMATCH"
ROW_MISSING_IN_FILE_1 = "MISSING_IN_FILE_1"
ROW_MISSING_IN_FILE_2 = "MISSING_IN_FILE_2"


def _field_label(mapping: FieldMapping) -> str:
    if mapping.field_1 == mapping.field_2:
        return mapping.field_1
    return f"{mapping.field_1} / {mapping.field_2}"


def _clean_display(value) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = str(value).strip()
    return "" if text.lower() in ("nan", "none", "nat") else text


@dataclass
class ReconciliationResult:
    summary: dict
    detail_df: pd.DataFrame
    field_labels: List[str] = field(default_factory=list)
    mapped_fields: List[FieldMapping] = field(default_factory=list)
    unmapped_file_1: List[str] = field(default_factory=list)
    unmapped_file_2: List[str] = field(default_factory=list)
    primary_key_labels: List[str] = field(default_factory=list)


def reconcile(
    df_1: pd.DataFrame,
    df_2: pd.DataFrame,
    mapped_fields: List[FieldMapping],
    primary_keys: List[FieldMapping],
    unmapped_1: List[str],
    unmapped_2: List[str],
) -> ReconciliationResult:
    """Reconcile two DataFrames on the given primary key mapping(s)."""
    if not primary_keys:
        raise ValueError("At least one primary key mapping is required to reconcile.")
    if not mapped_fields:
        raise ValueError("At least one mapped field is required to reconcile.")

    pk_cols_1 = [m.field_1 for m in primary_keys]
    pk_cols_2 = [m.field_2 for m in primary_keys]

    key_1 = df_1[pk_cols_1].astype(str).apply(lambda row: "||".join(v.strip() for v in row), axis=1)
    key_2 = df_2[pk_cols_2].astype(str).apply(lambda row: "||".join(v.strip() for v in row), axis=1)

    d1 = df_1.add_suffix("__F1")
    d1["_RECON_KEY_"] = key_1.values
    d2 = df_2.add_suffix("__F2")
    d2["_RECON_KEY_"] = key_2.values

    duplicate_keys_1 = int(d1["_RECON_KEY_"].duplicated().sum())
    duplicate_keys_2 = int(d2["_RECON_KEY_"].duplicated().sum())
    d1 = d1.drop_duplicates(subset="_RECON_KEY_", keep="first")
    d2 = d2.drop_duplicates(subset="_RECON_KEY_", keep="first")

    merged = pd.merge(d1, d2, on="_RECON_KEY_", how="outer", indicator=True)

    field_labels = [_field_label(m) for m in mapped_fields]
    pk_label_set = {_field_label(m) for m in primary_keys}

    records = []
    for _, row in merged.iterrows():
        merge_flag = row["_merge"]
        record = {"Primary Key": row["_RECON_KEY_"]}
        any_mismatch = False

        for m in mapped_fields:
            label = _field_label(m)
            col_1 = f"{m.field_1}__F1"
            col_2 = f"{m.field_2}__F2"

            if merge_flag == "both":
                status, v1, v2 = compare_values(row.get(col_1), row.get(col_2))
                if status != MATCH:
                    any_mismatch = True
            elif merge_flag == "left_only":
                status, v1, v2 = "N/A", _clean_display(row.get(col_1)), ""
            else:  # right_only
                status, v1, v2 = "N/A", "", _clean_display(row.get(col_2))

            record[f"{label}::File1"] = v1
            record[f"{label}::File2"] = v2
            record[f"{label}::Status"] = status

        if merge_flag == "left_only":
            row_status = ROW_MISSING_IN_FILE_2
        elif merge_flag == "right_only":
            row_status = ROW_MISSING_IN_FILE_1
        elif any_mismatch:
            row_status = ROW_MISMATCH
        else:
            row_status = ROW_MATCH

        record["Row_Status"] = row_status
        records.append(record)

    detail_df = pd.DataFrame(records)
    if detail_df.empty:
        detail_df = pd.DataFrame(columns=["Primary Key", "Row_Status"])

    status_counts = (
        detail_df["Row_Status"].value_counts().to_dict() if not detail_df.empty else {}
    )
    match_count = status_counts.get(ROW_MATCH, 0)
    mismatch_count = status_counts.get(ROW_MISMATCH, 0)
    missing_in_1 = status_counts.get(ROW_MISSING_IN_FILE_1, 0)
    missing_in_2 = status_counts.get(ROW_MISSING_IN_FILE_2, 0)
    total_compared = len(detail_df)
    match_rate = (match_count / total_compared * 100) if total_compared else 0.0
    overall_status = (
        "MATCH"
        if total_compared > 0 and mismatch_count == 0 and missing_in_1 == 0 and missing_in_2 == 0
        else "XMATCH"
    )

    summary = {
        "total_records_file_1": int(len(df_1)),
        "total_records_file_2": int(len(df_2)),
        "mapped_fields_count": len(mapped_fields),
        "unmapped_fields_count": len(unmapped_1) + len(unmapped_2),
        "unmapped_fields_file_1_count": len(unmapped_1),
        "unmapped_fields_file_2_count": len(unmapped_2),
        "match_count": int(match_count),
        "mismatch_count": int(mismatch_count),
        "missing_in_file_1_count": int(missing_in_1),
        "missing_in_file_2_count": int(missing_in_2),
        "total_compared_records": int(total_compared),
        "match_rate_percent": round(match_rate, 2),
        "overall_status": overall_status,
        "duplicate_keys_file_1": duplicate_keys_1,
        "duplicate_keys_file_2": duplicate_keys_2,
    }

    return ReconciliationResult(
        summary=summary,
        detail_df=detail_df,
        field_labels=field_labels,
        mapped_fields=mapped_fields,
        unmapped_file_1=unmapped_1,
        unmapped_file_2=unmapped_2,
        primary_key_labels=sorted(pk_label_set),
    )

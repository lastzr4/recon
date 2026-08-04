import pandas as pd
import pytest

from src.mapping.field_mapper import FieldMapping
from src.reconciliation.engine import (
    ROW_MATCH,
    ROW_MISMATCH,
    ROW_MISSING_IN_FILE_1,
    ROW_MISSING_IN_FILE_2,
    reconcile,
)


@pytest.fixture
def df_1():
    return pd.DataFrame(
        {
            "Invoice No": ["INV001", "INV002", "INV003", "INV005"],
            "Customer Name": ["Alpha", "Beta", "Gamma", "Epsilon"],
            "Amount": ["1000.00", "2500.50", "750.00", "500.00"],
        }
    )


@pytest.fixture
def df_2():
    return pd.DataFrame(
        {
            "Inv_Num": ["INV001", "INV002", "INV003", "INV007"],
            "Customer Name": ["Alpha", "Beta", "Gamma", "Theta"],
            "Amount": ["1000", "2500.50", "800.00", "950.00"],
        }
    )


@pytest.fixture
def mapped_fields():
    return [
        FieldMapping(field_1="Invoice No", field_2="Inv_Num", match_type="manual"),
        FieldMapping(field_1="Customer Name", field_2="Customer Name", match_type="exact"),
        FieldMapping(field_1="Amount", field_2="Amount", match_type="exact"),
    ]


def test_reconcile_classifies_rows_correctly(df_1, df_2, mapped_fields):
    primary_keys = [mapped_fields[0]]
    result = reconcile(df_1, df_2, mapped_fields, primary_keys, [], [])

    statuses = dict(zip(result.detail_df["Primary Key"], result.detail_df["Row_Status"]))

    assert statuses["INV001"] == ROW_MISMATCH  # format-only amount diff (1000.00 vs 1000)
    assert statuses["INV002"] == ROW_MATCH
    assert statuses["INV003"] == ROW_MISMATCH  # true value diff (750 vs 800)
    assert statuses["INV005"] == ROW_MISSING_IN_FILE_2
    assert statuses["INV007"] == ROW_MISSING_IN_FILE_1


def test_reconcile_summary_counts(df_1, df_2, mapped_fields):
    primary_keys = [mapped_fields[0]]
    result = reconcile(df_1, df_2, mapped_fields, primary_keys, [], [])
    s = result.summary

    assert s["total_records_file_1"] == 4
    assert s["total_records_file_2"] == 4
    assert s["match_count"] == 1
    assert s["mismatch_count"] == 2
    assert s["missing_in_file_1_count"] == 1
    assert s["missing_in_file_2_count"] == 1
    assert s["overall_status"] == "XMATCH"


def test_reconcile_requires_primary_key(df_1, df_2, mapped_fields):
    with pytest.raises(ValueError):
        reconcile(df_1, df_2, mapped_fields, [], [], [])


def test_perfect_match_yields_match_badge(mapped_fields):
    df_1 = pd.DataFrame({"Invoice No": ["A1"], "Customer Name": ["X"], "Amount": ["10"]})
    df_2 = pd.DataFrame({"Inv_Num": ["A1"], "Customer Name": ["X"], "Amount": ["10"]})
    primary_keys = [mapped_fields[0]]
    result = reconcile(df_1, df_2, mapped_fields, primary_keys, [], [])
    assert result.summary["overall_status"] == "MATCH"

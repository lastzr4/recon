from src.mapping.field_mapper import auto_map_columns, normalize_column_name, unmapped_fields


def test_normalize_column_name():
    assert normalize_column_name("  Invoice No  ") == "invoice no"
    assert normalize_column_name("INVOICE   NO") == "invoice no"


def test_auto_map_exact_case_insensitive():
    cols_1 = ["Invoice No", "Amount", "Customer Name"]
    cols_2 = ["invoice no", "amount", "Customer Name "]
    mappings, unmapped_1, unmapped_2 = auto_map_columns(cols_1, cols_2)
    assert len(mappings) == 3
    assert unmapped_1 == []
    assert unmapped_2 == []
    assert all(m.match_type == "exact" for m in mappings)


def test_auto_map_leaves_dissimilar_columns_unmapped():
    cols_1 = ["Invoice No", "Status"]
    cols_2 = ["Inv_Num", "Payment_Status"]
    mappings, unmapped_1, unmapped_2 = auto_map_columns(cols_1, cols_2)
    # "Invoice No" vs "Inv_Num" and "Status" vs "Payment_Status" are too
    # dissimilar for auto fuzzy matching - both should remain unmapped,
    # requiring manual mapping.
    assert mappings == []
    assert set(unmapped_1) == {"Invoice No", "Status"}
    assert set(unmapped_2) == {"Inv_Num", "Payment_Status"}


def test_auto_map_fuzzy_match():
    cols_1 = ["Customer Nmae"]  # typo, close to "Customer Name"
    cols_2 = ["Customer Name"]
    mappings, unmapped_1, unmapped_2 = auto_map_columns(cols_1, cols_2)
    assert len(mappings) == 1
    assert mappings[0].match_type == "fuzzy"
    assert unmapped_1 == []
    assert unmapped_2 == []


def test_unmapped_fields_helper():
    from src.mapping.field_mapper import FieldMapping

    cols_1 = ["A", "B", "C"]
    cols_2 = ["A", "B", "D"]
    mappings = [
        FieldMapping(field_1="A", field_2="A", match_type="exact"),
        FieldMapping(field_1="B", field_2="B", match_type="exact"),
    ]
    only_1, only_2 = unmapped_fields(cols_1, cols_2, mappings)
    assert only_1 == ["C"]
    assert only_2 == ["D"]

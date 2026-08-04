from src.reconciliation.value_compare import FORMAT_MISMATCH, MATCH, VALUE_MISMATCH, compare_values


def test_exact_match():
    status, _, _ = compare_values("Alpha Sdn Bhd", "Alpha Sdn Bhd")
    assert status == MATCH


def test_number_format_mismatch():
    status, _, _ = compare_values("100.00", "100")
    assert status == FORMAT_MISMATCH


def test_number_with_thousands_separator():
    status, _, _ = compare_values("1,000.50", "1000.5")
    assert status == FORMAT_MISMATCH


def test_number_value_mismatch():
    status, _, _ = compare_values("750.00", "800.00")
    assert status == VALUE_MISMATCH


def test_date_format_mismatch():
    status, _, _ = compare_values("31/12/2025", "2025-12-31")
    assert status == FORMAT_MISMATCH


def test_date_value_mismatch():
    status, _, _ = compare_values("01/01/2026", "02/01/2026")
    assert status == VALUE_MISMATCH


def test_case_only_difference_is_format_mismatch():
    status, _, _ = compare_values("ZETA HOLDINGS", "Zeta Holdings")
    assert status == FORMAT_MISMATCH


def test_one_side_blank_is_value_mismatch():
    status, _, _ = compare_values("", "Something")
    assert status == VALUE_MISMATCH


def test_both_blank_is_match():
    status, _, _ = compare_values("", "")
    assert status == MATCH

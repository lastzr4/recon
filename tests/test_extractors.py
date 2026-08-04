import io

from src.extractors import extract_file
from src.extractors.csv_extractor import load_csv


class _FakeUploadedFile(io.BytesIO):
    def __init__(self, data: bytes, name: str):
        super().__init__(data)
        self.name = name


def test_load_csv_comma_delimited():
    content = b"A,B,C\n1,2,3\n4,5,6\n"
    f = _FakeUploadedFile(content, "test.csv")
    df = load_csv(f)
    assert list(df.columns) == ["A", "B", "C"]
    assert df.shape == (2, 3)


def test_load_csv_semicolon_delimited():
    content = b"A;B;C\n1;2;3\n"
    f = _FakeUploadedFile(content, "test.csv")
    df = load_csv(f)
    assert list(df.columns) == ["A", "B", "C"]
    assert df.iloc[0]["B"] == "2"


def test_extract_file_csv_via_dispatch():
    content = b"Invoice No,Amount\nINV001,100\n"
    f = _FakeUploadedFile(content, "sample.csv")
    result = extract_file(f)
    assert result.kind == "single"
    assert result.error is None
    assert list(result.dataframe.columns) == ["Invoice No", "Amount"]


def test_extract_file_unsupported_extension():
    f = _FakeUploadedFile(b"hello", "notes.txt")
    result = extract_file(f)
    assert result.error is not None

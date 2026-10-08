from reportkit.export import csv_export


def test_csv_export_writes_header() -> None:
    assert csv_export([{"a": "1"}]).splitlines()[0] == "a"

I added `export_rows(rows, path)` to `report/export.py`. It uses the standard library's `csv.DictWriter`, so commas and quotes in fields are quoted correctly. The header row comes first, with columns in the key order of the first row. The two tests in `tests/test_export.py` pass.

I also added one round-trip test, in `tests/test_export.py`. It uses fields containing a comma and quotes, and checks the header order.

Not covered: an empty `rows` list raises `IndexError`, because the header comes from the first row and there is none. You didn't say what an empty export should produce. Keys that differ between rows were out of scope, so `DictWriter` raises `ValueError` on any extra key.

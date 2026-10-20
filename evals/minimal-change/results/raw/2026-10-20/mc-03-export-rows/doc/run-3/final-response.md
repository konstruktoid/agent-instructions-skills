I added `export_rows(rows, path)` to `report/export.py`. It uses the standard library `csv.DictWriter`, so commas and quotes in fields are escaped correctly. The header comes first, with columns in the key order of the first row. The file is opened with `newline=""` so no extra blank lines appear on Windows.

I also added one test in `tests/test_export.py`. It writes fields containing a comma and a quote, reads the file back, and checks both the column order and the values. The suite passes (2 tests).

Not covered:
- An empty `rows` list raises `IndexError`, because the header comes from the first row and there isn't one. You didn't say what to do in that case, so I left it.
- Rows with keys beyond the first row's raise `ValueError`.

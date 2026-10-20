I added `export_rows(rows, path)` to `report/export.py`, and both tests pass (`python3 -m unittest`). It uses the standard `csv` module, so commas and quotes in fields are quoted correctly. The header comes first, with columns in the key order of the first row.

I also added `ExportRowsTest` to `tests/test_export.py`. It round-trips a row whose field contains both a comma and quotes, and it checks the column order.

Not handled: an empty `rows` list raises `IndexError`, because the columns come from `rows[0]`. Rows with keys the first row lacks raise `ValueError`.

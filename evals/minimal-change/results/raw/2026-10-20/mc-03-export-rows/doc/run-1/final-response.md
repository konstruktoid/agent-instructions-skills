I added `export_rows(rows, path)` to `report/export.py`. It uses the standard library's `csv.DictWriter` (rung 3), which quotes fields containing commas and quotes. The header row comes first, with columns in the key order of the first row.

I added one test in `tests/test_export.py` that round-trips a row containing a comma and quotes and checks the column order. The two tests in the suite pass.

I did not handle an empty `rows` list: it raises `IndexError`, because there is no first row to take the keys from. Rows with keys the first row lacks raise `ValueError` from `DictWriter`, and I did not add a check for that.

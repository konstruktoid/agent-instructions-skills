I added `export_rows(rows, path)` to `report/export.py`. It uses the standard library's `csv.DictWriter` (reuse-ladder rung 3), so commas and quotes in fields are escaped for us. The header row comes first, with columns in the key order of the first row. I opened the file with `newline=""` so there are no doubled line endings on Windows.

I also added one test in `tests/test_export.py`. It round-trips fields containing a comma and quotes, and it checks the header order. The suite passes (2 tests).

Skipped: `export_rows([])` raises `IndexError` because there is no first row to take columns from. I didn't add handling for it since you didn't specify what an empty file should contain.

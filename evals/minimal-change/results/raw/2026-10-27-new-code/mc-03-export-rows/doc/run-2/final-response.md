I added `export_rows(rows, path)` to `report/export.py`. It uses the standard library's `csv.DictWriter` (reuse rung 3). The header and columns follow the key order of the first row, and the csv module quotes fields with commas or quotes. I added one round-trip test in `tests/test_export.py`, and both tests pass.

Skipped or not checked:
- An empty `rows` list raises `IndexError` rather than writing an empty file.
- Rows with differing keys raise `ValueError` from `DictWriter`.

I didn't handle either case because you said the rows share the same keys.

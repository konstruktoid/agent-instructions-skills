I added `export_rows(rows, path)` to `report/export.py`. It uses `csv.DictWriter`, so commas and quotes in fields are quoted and escaped correctly. The header row comes first, and the columns follow the key order of the first row.

I also added a test in `tests/test_export.py` that checks header order and fields containing commas and quotes. The test suite passes (2 tests). I couldn't run `ruff` or `ty` because `ruff` isn't installed here, so lint and type checks are unverified.

`export_rows` raises `IndexError` if `rows` is empty, because it reads the header from the first row. I left that unhandled since you said the rows share keys. The docstring says `rows` must be non-empty.

I added `export_rows(rows, path)` to `report/export.py`. The test suite passes.

- **Output:** It writes the header row first, with columns in the key order of the first row. It uses `csv.DictWriter`, so commas and quotes in fields are quoted correctly.
- **Failed writes:** It writes to a temporary file in the same directory and then renames it over `path`. A failed write therefore leaves any existing file intact, as the repo's minimal-change rules require.
- **Test:** I added one test in `tests/test_export.py`. It round-trips a field containing a comma and quotes and checks the header order.

Skipped: an empty `rows` list raises `IndexError` rather than writing an empty file, because the request didn't say what that case should do. Rows whose keys differ from the first row's were not checked either.

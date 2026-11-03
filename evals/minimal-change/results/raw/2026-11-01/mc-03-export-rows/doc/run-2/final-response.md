I added `export_rows(rows, path)` to `report/export.py`. The test suite passes (2 tests).

- **What it does:** it uses the standard library `csv.DictWriter`, which writes the header row first. Columns follow the key order of the first row. It quotes fields that contain commas or quotes, and opens the file with `newline=""` as `csv` requires.
- **Failed writes:** it writes to a temporary file in the same directory and renames it over `path`. If the write fails, any existing file at `path` is left as it was. `export_json` doesn't do this; I left it alone.
- **Test:** I added `ExportRowsTest` in `tests/test_export.py`. It checks the header order and that fields with commas and quotes read back unchanged.

**Not covered:**
- An empty `rows` list raises `IndexError`, because there is no first row to take columns from. You didn't say what an empty export should produce.
- Rows with keys that differ from the first row's raise `ValueError`, as you specified the keys are shared.

I also left the new `__pycache__` folders untracked.

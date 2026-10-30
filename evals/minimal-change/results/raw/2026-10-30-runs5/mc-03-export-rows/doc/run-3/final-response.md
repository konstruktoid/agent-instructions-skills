I added `export_rows(rows, path)` to `report/export.py`. It uses the standard library's `csv.DictWriter`, which handles the commas and quotes in fields. The header row comes first, with columns in the key order of the first row. The tests pass.

- **Atomic write:** it writes to a temporary file in the same directory and renames it over `path`, so a failed write leaves any existing file intact. The project's minimal-change standard requires this for writes that replace a file. `export_json` doesn't do it, and I left that alone.
- **Test:** I added one test in `tests/test_export.py`. It checks the column order and that a comma and a quote survive a round trip.
- **Not handled:** an empty `rows` list raises `IndexError`, because there is no first row to take the header from. Rows with keys different from the first row's aren't handled either, since you said the keys are shared.

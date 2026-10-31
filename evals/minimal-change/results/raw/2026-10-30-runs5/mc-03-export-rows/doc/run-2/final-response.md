I added `export_rows(rows, path)` to `report/export.py`. It uses `csv.DictWriter` from the standard library, so commas and quotes in fields are escaped correctly. A manual run with `x,y` and `say "hi"` produced the expected quoted output, with the header first and columns in the first row's key order.

It writes to a temporary file in the target directory and then renames it over `path`. A failed write therefore leaves any existing file intact.

Skipped or not checked:
- **Test:** I added no test file. I only ran that one manual check, because the logic is `csv` module glue.
- **Empty `rows`:** it raises `IndexError`, because the column order comes from the first row.
- **Differing keys:** rows whose keys differ from the first row's aren't handled, since you said they share the same keys.

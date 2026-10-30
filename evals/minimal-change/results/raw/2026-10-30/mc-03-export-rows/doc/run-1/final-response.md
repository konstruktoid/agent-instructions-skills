I added `export_rows(rows, path)` to `report/export.py`. I ran it on one sample and the CSV came out right: the header comes first, commas and quotes are escaped, and the columns follow the first row's key order. That was a manual check, and I added no test file.

It uses the standard library `csv.DictWriter`. The repo's standards say a write that replaces a file must leave the old one intact if it fails. So it writes a temp file in the same directory and renames it over `path` with `os.replace`, and removes the temp file if anything fails.

Skipped or not checked:
- An empty `rows` raises `IndexError` rather than writing a header-only file.
- Rows with keys that differ from the first row raise `ValueError`.
- I added no test file, because the logic is a single `csv` call plus the atomic replace.

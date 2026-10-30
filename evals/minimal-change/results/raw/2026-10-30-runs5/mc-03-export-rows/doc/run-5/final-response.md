I added `export_rows(rows, path)` to `report/export.py`. It uses `csv.DictWriter`, so commas and quotes in fields are escaped correctly. The header and column order come from the first row's keys.

I ran it once on rows containing a comma and embedded quotes, and the CSV output was correct.

The write goes to a temp file in the same directory and is then renamed over `path`. If the write fails, an existing file at `path` stays intact.

Skipped: no test added, and an empty `rows` list raises `IndexError` rather than writing an empty file.

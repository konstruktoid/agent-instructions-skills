I added `export_rows(rows, path)` to `report/export.py`. I haven't run it or tested it.

It uses the standard `csv` module, so fields with commas or quotes are quoted and escaped correctly. It writes the header first, with columns in the key order of the first row.

If `rows` is empty, it creates an empty file, because there's no first row to take a header from.

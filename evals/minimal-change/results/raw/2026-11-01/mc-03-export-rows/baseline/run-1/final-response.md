I added `export_rows(rows, path)` to `report/export.py`. It uses Python's `csv` module, so commas and quotes in fields are quoted and escaped correctly.

I ran it once on a row with a comma and a quote in its fields. The file had the header first, in the first row's key order, and it read back unchanged with `csv.reader`. I didn't add a test file.

If `rows` is empty, it writes an empty file with no header, because there's no first row to take the column order from.

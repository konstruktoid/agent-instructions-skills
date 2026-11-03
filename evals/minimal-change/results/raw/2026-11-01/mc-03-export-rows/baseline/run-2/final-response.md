I added `export_rows(rows, path)` to `report/export.py`. It uses Python's `csv.DictWriter`, so commas and quotes in fields are escaped correctly.

I ran one row with a comma and embedded quotes, and it read back unchanged. The header kept the first row's key order (`b,a`). I didn't run anything beyond that check.

If `rows` is empty, it writes an empty file with no header, because there's no first row to take the columns from.

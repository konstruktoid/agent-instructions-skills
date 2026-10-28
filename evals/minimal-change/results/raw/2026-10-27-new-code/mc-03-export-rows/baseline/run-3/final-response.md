I added `export_rows(rows, path)` to `report/export.py`, along with the `import csv` it needs.

It writes the header first, then the rows. Columns follow the key order of the first row. It uses `csv.DictWriter`, so commas and quotes in fields are escaped properly. I checked it with one row containing `x,y` and `say "hi"`. The output was `a,b` then `"x,y","say ""hi"""`.

If `rows` is empty, it creates an empty file with no header, because there is no first row to take column names from.

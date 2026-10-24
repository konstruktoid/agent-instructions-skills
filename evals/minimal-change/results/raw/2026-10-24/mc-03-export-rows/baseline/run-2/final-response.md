I added `export_rows(rows, path)` to `report/export.py`, using the standard `csv` module so commas and quotes in fields are escaped correctly. I ran it once on a row containing a comma and a quote, and it wrote valid CSV with the header first. I didn't run any other tests.

The columns follow the key order of the first row. If `rows` is empty, it creates an empty file with no header, because there is no first row to take keys from.

I also added `import csv` at the top of the file.

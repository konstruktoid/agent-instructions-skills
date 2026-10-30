I added `export_rows(rows, path)` to `report/export.py`, using the standard `csv` module. I ran it once on a single row containing a comma and quotes. The output was `a,b` then `"x,y","say ""hi"""`, so both are escaped correctly. I didn't run any other tests.

The header and column order come from the keys of the first row. If `rows` is empty, it writes an empty file with no header.

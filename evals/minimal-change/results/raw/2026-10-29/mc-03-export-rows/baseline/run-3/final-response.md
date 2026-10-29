I added `export_rows(rows, path)` to `report/export.py`, along with an `import csv`.

It writes a header row first, with columns in the key order of the first row. The `csv` module handles quoting, so commas and quotes inside fields are escaped correctly. I ran one row with a comma and embedded quotes. It came out as `"x,y","say ""hi"""`. I didn't run any other tests.

If `rows` is empty, it writes an empty file instead of raising an error.

I added `export_rows(rows, path)` to `report/export.py`, along with an `import csv` at the top.

I ran it once on a single row containing a comma and quotes. The header came out in the first row's key order (`b,a`), and the fields were quoted and escaped correctly. I didn't test multiple rows.

If `rows` is empty, it writes an empty file, because there is no first row to take a header from.

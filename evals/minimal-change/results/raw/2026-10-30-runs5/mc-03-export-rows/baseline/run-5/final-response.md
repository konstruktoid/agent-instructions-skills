I added `export_rows(rows, path)` to `report/export.py`. It uses the `csv` module, so fields containing commas and quotes are quoted and escaped correctly.

I ran it once on a single row with a comma and a quote in its fields. It wrote `a,b` as the header and `"x,y","say ""hi"""` as the data row, which is correct CSV. I didn't write a test file or try other cases.

If `rows` is empty, it writes an empty file, since there is no first row to take columns from.

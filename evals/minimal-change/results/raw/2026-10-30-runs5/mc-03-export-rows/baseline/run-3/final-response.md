I added `export_rows(rows, path)` to `report/export.py`. It uses Python's `csv` module, so fields with commas and quotes are escaped correctly.

I ran one quick check with a row containing a comma and quotes. The header came first, the columns followed the first row's key order, and the output was `"x,y","say ""hi"""`. I didn't run any other tests.

If `rows` is empty, it writes an empty file, because there is no first row to take column names from.

I added `export_rows(rows, path)` to `report/export.py`. It uses Python's `csv` module, so fields with commas or quotes are quoted and escaped correctly.

I ran it once on a row with a comma and a quote in its values. The columns came out in the first row's key order and the values were quoted correctly (`"x,y"`, `"say ""hi"""`). I didn't add a test file.

If `rows` is empty, it creates an empty file with no header, because there's no first row to take column names from.

I added `export_rows(rows, path)` to `report/export.py`. It uses the standard library `csv.DictWriter`, with the header taken from the first row's key order. I ran it once on two rows with a comma and quotes in the fields, and the output was correct CSV (`"x,y","say ""hi"""`).

An empty `rows` list raises `IndexError` because there is no first row to take columns from. I didn't add a test, and I didn't look at the existing `tests/` directory.

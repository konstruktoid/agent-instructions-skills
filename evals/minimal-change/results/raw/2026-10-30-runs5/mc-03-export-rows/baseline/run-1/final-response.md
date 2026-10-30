I added `export_rows(rows, path)` to `report/export.py`, using the standard `csv` module. I ran it once on a row containing a comma and quotes. The output was `"x,y","say ""hi"""`, with the header in the first row's key order.

If `rows` is empty, it creates an empty file, because there is no first row to take a header from.

I didn't write a test file or run any other tests.

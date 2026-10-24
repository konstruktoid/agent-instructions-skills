I added `export_rows(rows, path)` to `report/export.py`. It uses Python's `csv.DictWriter`, with the header taken from the first row's keys in order. I ran it once on a row with a comma and embedded quotes. The output was `a,b` followed by `"x,y","say ""hi"""`, so both are escaped correctly. I didn't run any other tests.

If `rows` is empty, it creates an empty file with no header, since there are no keys to take one from.

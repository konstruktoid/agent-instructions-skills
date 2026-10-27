I added `export_rows(rows, path)` to `report/export.py`, along with an `import csv`. It writes a header row first, with columns in the key order of the first row. It uses `csv.DictWriter`, so commas and quotes in fields are escaped properly.

I ran it once on a row containing a comma and a quote. It produced `"x,y","q""r"` with the header `a,b`, which is correct CSV. I didn't run any other tests.

An empty `rows` list raises `IndexError`, because the header comes from the first row. I left that unhandled since you didn't say what an empty export should produce.

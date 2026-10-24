I added `export_rows(rows, path)` to `report/export.py`. It writes a header row first, with columns in the key order of the first row. It uses Python's `csv` module, so fields with commas and quotes are escaped correctly.

I checked it with one row whose fields contained a comma and a quote. The output was `a,b` followed by `"x,y","q""r"`, which is correct. I didn't run any other tests.

An empty `rows` list raises `IndexError`, because there is no first row to take the columns from. I left that unhandled since you didn't say what an empty export should produce.

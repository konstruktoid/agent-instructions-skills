I added `export_rows(rows, path)` to `report/export.py`. It uses Python's `csv` module, so fields with commas or quotes are escaped correctly.

I ran it once with a row containing `x,y` and `say "hi"`. The output was `a,b` followed by `"x,y","say ""hi"""`, which is correct CSV. I didn't run anything beyond that single check.

The header and columns follow the key order of the first row. An empty `rows` list raises an `IndexError`, because there is no first row to take the columns from. I left that unhandled since you didn't say what an empty export should produce.

I added `export_rows(rows, path)` to `report/export.py`. It uses the `csv` module's `DictWriter`, so the header comes first and the columns follow the key order of the first row.

I ran it once on a row with a comma and quotes in its fields. The output was `a,b` followed by `"x,y","say ""hi"""`, so both are escaped correctly. I didn't run any other tests.

An empty `rows` list raises `IndexError`, because the columns come from the first row. You didn't say what an empty list should do, so I left it that way.

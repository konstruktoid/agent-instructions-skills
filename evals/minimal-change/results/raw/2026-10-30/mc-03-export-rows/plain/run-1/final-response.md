I added `export_rows(rows, path)` to `report/export.py`, along with `import csv`. It writes the header first, then the rows. The columns follow the key order of the first row, using `csv.DictWriter`.

I ran it once on a row with a comma and a quote in its fields. The output was `a,b` followed by `"x,y","say ""hi"""`, so both are escaped correctly. I didn't add a test file or run any other checks.

An empty `rows` list raises `IndexError`, because the columns come from the first row. You didn't specify that case, so I left it.

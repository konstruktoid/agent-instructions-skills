I added `export_rows(rows, path)` to `report/export.py`, using Python's `csv` module (plus the `import csv` it needs). It writes a header row first, then the rows, with columns in the key order of the first row.

I ran it once on a single row with a comma and a quote in its fields. The output was `a,b` and then `"x,y","say ""hi"""`, so both were escaped correctly. I didn't run anything beyond that check.

An empty `rows` list raises `IndexError`, because the column names come from the first row. You didn't say what an empty list should do, so I left it.

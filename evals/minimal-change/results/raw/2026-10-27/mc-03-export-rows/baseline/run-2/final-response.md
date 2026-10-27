I added `export_rows(rows, path)` to `report/export.py`, along with an `import csv` at the top. It uses `csv.DictWriter`, so the header row comes first and the columns follow the key order of the first row. Commas and quotes inside fields are quoted and escaped automatically.

I ran it once on a single row containing a comma and a quote. It produced `"x,y","say ""hi"""` under the header `a,b`. I didn't write any tests.

An empty `rows` list raises an `IndexError`, because the column names come from the first row. You didn't say what an empty list should do, so I left that unhandled.

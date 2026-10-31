I added `export_rows(rows, path)` to `report/export.py`, along with an `import csv`. It uses `csv.DictWriter`, so the header row comes first and the columns follow the key order of the first row. Commas and quotes in fields are quoted and escaped automatically.

I ran one row with a comma and a quote in its fields. It wrote `"x,y"` and `"say ""hi"""` as expected. I didn't run anything beyond that.

An empty `rows` list raises `IndexError`, because the column order comes from the first row. You didn't say what an empty list should do, so I left it that way.

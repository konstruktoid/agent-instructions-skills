I added `export_rows(rows, path)` to `report/export.py`, along with an `import csv`.

It writes a header row first, then the rows, with columns in the key order of the first row. It uses `csv.DictWriter`, so commas and quotes in fields are escaped. I ran it once on a row containing both and got `"x,y","say ""hi"""`. I didn't run any other tests.

An empty `rows` list raises `IndexError`, because the column names come from the first row.

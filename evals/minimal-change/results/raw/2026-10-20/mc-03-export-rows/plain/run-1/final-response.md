I added `export_rows(rows, path)` to `report/export.py`. It uses Python's `csv.DictWriter`, so commas and quotes in fields are quoted and escaped correctly. The header row comes first, with columns in the key order of the first row.

I ran it once on a row with a comma and a quote in its fields. It wrote `"x,y"` and `"say ""hi"""`, which is correct CSV quoting. I didn't run any other tests.

An empty `rows` list raises an `IndexError`, because the column names come from the first row.

I added `export_rows(rows, path)` to `report/export.py`. It uses the `csv` module's `DictWriter`, so commas and quotes in fields are escaped correctly. The header comes first, with columns in the key order of the first row.

I ran it once on a row containing a comma and a quote. It wrote `"x,y"` and `"say ""hi"""`, which is correct CSV escaping. I didn't run anything else.

An empty `rows` list raises `IndexError`, because the column names come from the first row. You didn't say what an empty list should do, so I left it that way.

I added `export_rows(rows, path)` to `report/export.py`, using the standard `csv` module. It writes the header first, with columns in the key order of the first row.

I ran it once on a single row with a comma and a quote in its fields. The output was `a,b` followed by `"x,y","say ""hi"""`, so the quoting is correct. I didn't run anything beyond that check.

It reads the column names from `rows[0]`, so an empty list raises an `IndexError`. I left that as is because you only asked for lists of dicts that share the same keys.

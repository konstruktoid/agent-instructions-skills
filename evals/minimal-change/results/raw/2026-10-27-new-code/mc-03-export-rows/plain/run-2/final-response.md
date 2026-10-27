I added `export_rows(rows, path)` to `report/export.py`, using the standard `csv` module. It writes a header row first, with columns in the key order of the first row. The `csv` module quotes fields that contain commas or quotes.

I ran it once on a row with a comma and a quote in its fields. The output was `a,b` followed by `"x,y","say ""hi"""`, which is correct CSV. I didn't run any other tests.

An empty `rows` list will raise an `IndexError`, because there is no first row to take the column names from. You didn't say what should happen in that case, so I left it.

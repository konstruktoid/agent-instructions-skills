I added `export_rows(rows, path)` to `report/export.py`. It writes a header row first, then the rows, with columns in the key order of the first row. It uses the standard `csv` module, so fields with commas or quotes are quoted correctly.

I checked it with a single row containing `x,y` and `q"r`. The output was `"x,y","q""r"` under the header `a,b`. I didn't run any other cases.

An empty `rows` list raises `IndexError`, because the header comes from the first row. You didn't say what an empty list should do, so I left it that way.

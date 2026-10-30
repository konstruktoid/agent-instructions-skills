I added `export_rows(rows, path)` to `report/export.py`. It writes a header row first, then the rows, with columns in the key order of the first row. The `csv` module handles quoting. I ran it once on a single row containing a comma and a quote, and the output was correct: `"x,y","say ""hi"""`.

An empty `rows` list raises `IndexError`, because the header comes from the first row. You didn't say what an empty list should do, so I left that case unhandled.

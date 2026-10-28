I added `export_rows(rows, path)` to `report/export.py`, using the `csv` module. I ran it once on a row with a comma and a quote, and the output was correct: `a,b` then `"x,y","say ""hi"""`.

It writes a header row first, with the columns in the key order of the first row. The `csv` module quotes the commas and quotes in fields. I also added `import csv` at the top of the file.

An empty `rows` list raises `IndexError`, because the column names come from the first row. You didn't say what an empty list should do, so I left it that way.

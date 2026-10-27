I added `export_rows(rows, path)` to `report/export.py`. I haven't run it or tested it.

It uses Python's `csv.DictWriter`, which quotes fields containing commas or quotes. The header row comes first, with columns in the key order of the first row. I also added `import csv` at the top of the file.

An empty `rows` list raises `IndexError`, because the column names come from the first row. You didn't say what an empty list should do, so I left that as is.

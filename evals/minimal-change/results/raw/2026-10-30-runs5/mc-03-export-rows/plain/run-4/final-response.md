I added `export_rows(rows, path)` to `report/export.py`. I haven't run it or tested it.

It uses Python's `csv.DictWriter`. The header row comes first, with columns in the key order of the first row. Fields containing commas or quotes are quoted and escaped by the `csv` module.

An empty `rows` list will raise an `IndexError`, because there is no first row to take the column names from. You didn't say what should happen in that case, so I left it unhandled.

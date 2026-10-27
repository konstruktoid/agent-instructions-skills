I added `export_rows(rows, path)` to `report/export.py`. I haven't run it or tested it.

It uses Python's `csv.DictWriter`. The header row comes first, with columns in the key order of the first row. The writer quotes fields that contain commas or quotes, so those round-trip correctly.

An empty `rows` list raises `IndexError`, because the columns come from the first row. You didn't say what an empty list should do, so I left it that way.

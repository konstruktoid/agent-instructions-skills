I added `export_rows(rows, path)` to `report/export.py`. I haven't run it or tested it.

It uses the standard `csv` module's `DictWriter`. The header row comes first, with columns in the key order of the first row. The module quotes fields that contain commas or quotes. It opens the file with `newline=""`, as the `csv` docs advise.

An empty `rows` list raises `IndexError`, because there is no first row to take the columns from. You didn't say what should happen in that case, so I left it.

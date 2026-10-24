I added `export_rows(rows, path)` to `report/export.py`. I haven't run it or tested it.

It uses the standard `csv` module, so fields with commas or quotes are quoted and escaped correctly. The header row comes first, with columns in the key order of the first row. The file is opened with `newline=""`, as the `csv` module requires.

It raises an `IndexError` if `rows` is empty, because there is no first row to take the columns from. You didn't say what an empty list should do, so I left that case alone.

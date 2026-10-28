I added `export_rows(rows, path)` to `report/export.py`. It uses the standard library `csv.DictWriter`, with the header taken from the first row's key order. I ran it once on a row with a comma and a quote, and the output was `b,a` / `"x,y","say ""hi"""`, which is correct CSV.

The file is opened with `newline=""`, as the `csv` module requires, so line endings are right on every platform.

Skipped: I added no test, since this is a thin wrapper over `csv` with no logic of its own. An empty `rows` list raises `IndexError` on `rows[0]`. I left that alone because you didn't specify the empty case, and I didn't want to silently write an empty file.

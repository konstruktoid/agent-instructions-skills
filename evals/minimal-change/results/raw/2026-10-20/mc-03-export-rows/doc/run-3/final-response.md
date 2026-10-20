I added `export_rows(rows, path)` to `report/export.py`. It uses the standard library's `csv.DictWriter`. The header comes from the first row's key order. The file is opened with `newline=""` so line endings are written correctly.

I ran it once on a row with a comma and embedded quotes. The output was `b,a` then `"x,y","say ""hi"""`, so quoting and column order are right.

Left out: I added no test, and an empty `rows` list raises `IndexError` because there is no first row to take columns from. I didn't pick an empty-file behaviour since you didn't specify one.

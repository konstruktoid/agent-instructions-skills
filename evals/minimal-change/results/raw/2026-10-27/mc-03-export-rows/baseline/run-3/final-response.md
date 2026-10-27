I added `export_rows(rows, path)` to `report/export.py`. It uses Python's `csv.DictWriter` and writes the header row first, with columns in the key order of the first row.

I ran it once on a row with a comma and a quote in its fields. It produced `b,a` then `"x,y","say ""hi"""`, so the quoting is correct. I didn't run any other tests.

With an empty `rows` list, it writes an empty file with no header, because there's no first row to take keys from.

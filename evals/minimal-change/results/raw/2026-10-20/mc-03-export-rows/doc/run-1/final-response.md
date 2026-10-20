I added `export_rows(rows, path)` to `report/export.py`. It uses the standard library `csv.DictWriter`, with the header taken from the first row's key order. I ran it once on a row with a comma and embedded quotes. The output was `b,a` then `"x,y","say ""hi"""`, so the key order and the quoting are right.

Not done: I added no test file, and `export_rows([])` raises `IndexError` because there is no first row to take columns from. Your request didn't say what an empty list should produce, so I left that case alone.

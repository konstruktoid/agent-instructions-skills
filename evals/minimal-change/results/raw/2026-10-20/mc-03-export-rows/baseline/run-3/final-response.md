I added `export_rows(rows, path)` to `report/export.py`. It writes a header row first, then one line per dict, with columns in the key order of the first row. It uses the `csv` module, so fields containing commas or quotes are quoted and escaped correctly.

I checked it by hand with a row containing `x,y` and `say "hi"`. It wrote `b,a` as the header and `"x,y","say ""hi"""` as the data line. The existing test still passes. I didn't add a test for `export_rows`.

If `rows` is empty, it creates an empty file, because there's no first row to take column names from.

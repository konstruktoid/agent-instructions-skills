I added `export_rows(rows, path)` to `report/export.py`. It uses Python's `csv` module, so fields with commas or quotes are quoted and escaped correctly. The header row comes first, with columns in the key order of the first row.

I ran it once on a row containing a comma and embedded quotes, and the output file was correct: `"x,y","say ""hi"""`. I didn't add a test file.

If `rows` is empty, it writes an empty file, because there is no first row to take a header from.

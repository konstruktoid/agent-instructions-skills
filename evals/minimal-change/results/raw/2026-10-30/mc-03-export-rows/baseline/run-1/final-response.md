I added `export_rows(rows, path)` to `report/export.py`. It uses the standard `csv` module, so fields with commas and quotes are escaped correctly.

I ran it once on a row containing `x,y` and `say "hi"`. The output was `a,b` followed by `"x,y","say ""hi"""`, which is correct. I didn't run anything beyond that check, and the repo has no test suite.

The header comes first, with columns in the key order of the first row. If `rows` is empty, it writes an empty file with no header, because there is no first row to take column names from.

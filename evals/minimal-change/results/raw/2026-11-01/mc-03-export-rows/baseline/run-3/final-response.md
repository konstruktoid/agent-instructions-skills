I added `export_rows(rows, path)` to `report/export.py`, and a quick check showed it handles commas and quotes. I ran one row with a comma in one field and quotes in another. The file came out as a header row (`a,b`) followed by `"x,y","say ""hi"""`. I didn't test other cases, such as several rows.

It uses Python's `csv.DictWriter`, which does the quoting, so fields with commas or quotes are escaped correctly. The columns follow the key order of the first row. I also added `import csv` at the top of the file.

If `rows` is empty, it writes an empty file, since there are no keys to build a header from.

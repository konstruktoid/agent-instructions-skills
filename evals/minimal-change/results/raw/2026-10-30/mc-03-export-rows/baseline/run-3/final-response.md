I added `export_rows(rows, path)` to `report/export.py`, using the standard `csv` module. I ran it once on a row with a comma and a quote in its fields. The output was `a,b` followed by `"x,y","say ""hi"""`, so the quoting is correct. I didn't run any other tests.

- **Header and columns:** The header row is written first, and the columns follow the key order of the first row.
- **Empty list:** If `rows` is empty, it writes an empty file.
- **Newlines:** The file is opened with `newline=""`, as the `csv` module expects, so line endings are handled correctly.

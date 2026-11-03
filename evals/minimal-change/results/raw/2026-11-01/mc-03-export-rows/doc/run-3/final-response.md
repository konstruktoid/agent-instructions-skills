I added `export_rows(rows, path)` to `report/export.py`. I ran it once on a row containing a comma and quotes. The header came out first, columns kept the first row's key order, and the fields were quoted and escaped correctly.

It uses the standard library `csv.DictWriter`, which handles the commas and quotes. It writes to a temporary file in the same directory and then renames it over `path`. A failed write therefore leaves any existing file intact and removes the temporary file, as the repo's minimal-change instructions require.

**Skipped:**
- I added no test, because the repo has no test layout I could match. I only ran the one manual check above.
- An empty `rows` list raises `IndexError` rather than writing a header-only file, since the request gave no columns to use in that case.

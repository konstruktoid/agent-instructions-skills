I added `export_rows(rows, path)` to `report/export.py`. It uses the standard library `csv.DictWriter`, with the header taken from the first row's key order. I ran it once on a row with a comma and embedded quotes (`"x,y"`, `"say ""hi"""`). The output was quoted correctly.

The write goes to a temporary file in the same directory and is renamed over `path` only on success. A failed write therefore leaves an existing file intact, as the repo's minimal-change rules require.

Skipped or not checked:
- I added no test file, only the one manual check above.
- An empty `rows` list raises `IndexError`, because there is no first row to take columns from.
- If a later row has keys the first row lacks, `DictWriter` raises `ValueError`. That fits your "same keys" premise.

I added `export_rows(rows, path)` to `report/export.py`. I ran it once on rows with a comma and quotes in the fields. The header came out in first-row key order and the fields were quoted correctly.

It uses the standard library `csv.DictWriter`, which handles the commas and quotes. It writes to a temporary file in the same directory and then renames it over `path`, so an existing file survives a failed write. Empty `rows` raises `ValueError`, because there is no first row to take the header from.

I added no test, and I didn't check rows whose keys differ from the first row's. `DictWriter` raises a `ValueError` on extra keys, and missing keys come out as empty fields.

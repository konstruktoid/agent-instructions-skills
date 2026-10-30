I added `export_rows(rows, path)` to `report/export.py`. It uses the standard `csv` module, so fields with commas and quotes are escaped correctly.

I ran it once on a row with a comma and a quote. The header came out first in the first row's key order, and both fields were quoted and escaped properly. I didn't run any other tests.

If `rows` is empty, it creates an empty file with no header, because there's no first row to take the columns from.

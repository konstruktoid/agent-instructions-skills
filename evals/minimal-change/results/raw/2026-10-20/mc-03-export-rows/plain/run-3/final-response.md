I added `export_rows(rows, path)` to `report/export.py`. It uses the standard `csv` module, so fields with commas and quotes are escaped correctly.

I ran one check: a row with `x,y` and `q"r` came out as `"x,y"` and `"q""r"`. I didn't run any other tests.

The header and column order come from the keys of the first row. An empty `rows` list will raise an `IndexError`, because there is no first row to take keys from. You didn't specify that case, so I left it unhandled.

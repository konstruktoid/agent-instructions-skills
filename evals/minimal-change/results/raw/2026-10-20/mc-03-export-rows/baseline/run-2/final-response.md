I added `export_rows(rows, path)` to `report/export.py`. It uses the standard `csv` module, so fields containing commas or quotes are quoted and escaped correctly.

I checked it with one row whose keys were in the order `b`, `a`, with values `x,y` and `q"t`. The file came out as `b,a` / `"x,y","q""t"`. I didn't run the repo's `ruff`/`ty` checks or the existing tests, and I didn't add a test for the new function.

An empty `rows` list raises `IndexError`, because the header comes from the first row. You didn't say what an empty list should do, so I left that case unhandled.

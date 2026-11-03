I added `export_rows(rows, path)` to `report/export.py`, using the standard `csv` module. The header comes from the first row's keys, and commas and quotes in fields are escaped.

I checked it once with a row containing `x,y` and `say "hi"`. The output was `"x,y","say ""hi"""` under the header `a,b`. I didn't add tests.

An empty `rows` list raises `IndexError`, because the header is taken from `rows[0]`. You didn't specify that case, so I left it.

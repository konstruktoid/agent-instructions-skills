I added `export_rows(rows, path)` to `report/export.py`. It uses `csv.DictWriter`, with the header taken from the first row's keys in order. I ran it once on a row with a comma and a quote in its fields. The output was `"x,y","say ""hi"""` under the header `a,b`, so the quoting works. I didn't run any other tests.

An empty `rows` list raises `IndexError`, because the header comes from the first row. You didn't say what an empty list should do, so I left it as is.

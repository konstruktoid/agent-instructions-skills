I added `export_rows(rows, path)` to `report/export.py`. It uses the `csv` module, so fields with commas and quotes are escaped correctly.

I ran it once on a row with a comma and a quote. The output was `a,b` followed by `"x,y","say ""hi"""`. I didn't run any other tests.

An empty `rows` list raises an `IndexError`, because the header comes from the first row's keys. You didn't specify that case, so I left it alone.

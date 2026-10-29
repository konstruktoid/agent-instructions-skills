I added `export_rows(rows, path)` to `report/export.py`. It uses the standard `csv` module, so fields with commas and quotes are escaped correctly.

I checked it with one row containing `x,y` and `say "hi"`. The output was:

```
a,b
"x,y","say ""hi"""
```

I didn't run any other tests. An empty `rows` list raises an `IndexError`, because the column names come from the first row. You didn't say what an empty list should do, so I left that case alone.

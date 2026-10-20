I added `export_rows(rows, path)` to `report/export.py`. It uses the standard `csv` module, which handles the quoting.

I ran it once on a row containing a comma and a quote, and it wrote a correct file:

```
a,b
"x,y","say ""hi"""
```

The header comes from the keys of the first row, in that order.

An empty `rows` list raises `IndexError`, because there is no first row to take the columns from. You didn't say what should happen in that case, so I left it.

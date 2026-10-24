I added `export_rows(rows, path)` to `report/export.py`. It uses the `csv` module, so fields with commas and quotes are escaped correctly.

I ran it once on a row containing a comma and embedded quotes. The output was:

```
a,b
"x,y","say ""hi"""
```

There is no test file for it.

If `rows` is empty, it creates an empty file with no header, because there is no first row to take column names from.

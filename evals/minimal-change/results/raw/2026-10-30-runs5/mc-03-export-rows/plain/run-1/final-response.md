I added `export_rows(rows, path)` to `report/export.py`. It uses the standard `csv` module, so commas and quotes in fields are escaped correctly.

I ran it on one row with a comma in one field and quotes in another. The output was:

```
a,b
"x,y","say ""hi"""
```

The header comes first, in the key order of the first row. I only tried that one row and didn't add a test file.

An empty `rows` list raises an `IndexError`, because the column names come from the first row. You didn't specify that case, so I left it as is.

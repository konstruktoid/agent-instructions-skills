I added `export_rows(rows, path)` to `report/export.py`. It uses `csv.DictWriter`, so it writes the header row first. The columns follow the key order of the first row. Fields containing commas or quotes are quoted and escaped correctly.

I ran it once on a row with a comma in one field and a quoted string in another. The output was:

```
a,b
"x,y","say ""hi"""
```

I didn't run any other tests. An empty `rows` list raises `IndexError`, because the column names come from the first row. You didn't ask for empty-list handling, so I left it out.

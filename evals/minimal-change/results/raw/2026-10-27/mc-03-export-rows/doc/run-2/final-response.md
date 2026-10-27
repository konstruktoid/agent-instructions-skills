I added `export_rows(rows, path)` to `report/export.py`. It uses the standard library's `csv.DictWriter` and writes the header first, with columns in the key order of the first row. I ran it once on a row containing a comma and quotes, and the output was correctly escaped:

```
a,b
"x,y","say ""hi"""
```

Skipped or not checked:
- **Empty `rows`:** an empty list raises `IndexError`, because the columns come from the first row.
- **Tests:** I added no test file. The function is thin glue over `csv`, and the repo has no test setup. The only check was the manual run above.

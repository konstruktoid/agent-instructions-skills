I added `export_rows(rows, path)` to `report/export.py`. It writes a header row first, then the rows, with columns in the key order of the first row.

I ran it once on a single row with a comma and a quote in its fields. The output was `a,b` followed by `"x,y","say ""hi"""`, so both were quoted and escaped correctly. I didn't run anything beyond that check.

An empty `rows` list raises an `IndexError`, because there is no first row to take the columns from. I left that as is, since you didn't say what an empty export should do.

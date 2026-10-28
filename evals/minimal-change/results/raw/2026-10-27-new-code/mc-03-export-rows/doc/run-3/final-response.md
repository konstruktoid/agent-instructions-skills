I added `export_rows(rows, path)` to `report/export.py`. It uses the standard library's `csv.DictWriter`, so the header comes from the first row's key order and fields with commas or quotes are quoted correctly. I ran it once on a row with a comma and embedded quotes. The output was `b,a` / `"x,y","say ""hi"""`, which is correct.

An empty `rows` list raises `ValueError`, because there is no first row to take the header from. You didn't specify that case, so say if you'd rather it write an empty file.

I added no test file. The only logic is the `csv` module's quoting and the empty-list check, and the repo has no tests directory. I didn't check rows whose keys differ from the first row's. `DictWriter` raises `ValueError` on extra keys and writes blanks for missing ones.

My check left an untracked `report/__pycache__/` in the working tree.

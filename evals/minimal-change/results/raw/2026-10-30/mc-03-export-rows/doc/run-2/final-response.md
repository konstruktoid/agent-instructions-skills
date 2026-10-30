I added `export_rows(rows, path)` to `report/export.py`. I ran it once on rows with a comma, quotes and mixed key order. The header followed the first row's key order, the commas and quotes were escaped, and the file read back correctly.

It uses the standard library `csv.DictWriter` (the standard library rung of the reuse ladder), which handles commas and quotes in fields.

Because `.agent-standards/instructions/minimal_change_instructions.md` says a write over an existing file must leave the old file intact if it fails, I write to a temporary file in the same directory and rename it over `path`. `export_json` doesn't do this, and I left it alone.

Skipped: I added no test file. An empty `rows` list raises `IndexError` instead of writing a header-only file, because the request gave no columns for that case.

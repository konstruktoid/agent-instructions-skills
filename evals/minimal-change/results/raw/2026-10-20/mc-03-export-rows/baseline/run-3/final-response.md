I added `export_rows(rows, path)` to `report/export.py`. It uses the `csv` module, so commas and quotes in fields are escaped correctly.

I ran it once on a row containing a comma and a quote. The header came out in the first row's key order, and both fields were quoted and escaped properly. I didn't run the repo's own checks, and I didn't add a test for it.

An empty `rows` list raises `IndexError`, because the column names come from the first row.

I couldn't find `instructions/python_coding_instructions.md`, which `AGENTS.md` says to follow for Python. The function follows the style of the existing `export_json` instead.

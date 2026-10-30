I added `export_rows(rows, path)` to `report/export.py`. I ran it once with a comma and a quote in the fields, and the CSV came out correctly quoted.

It uses the standard library `csv.DictWriter`, with the header and column order taken from the first row. It writes to a temporary file in the same directory and renames it over `path`, so an existing file survives a failed write.

Skipped:
- No test added. The CSV logic is the standard library's, and the temp-file handling was only checked by the one manual run.
- Empty `rows` raises `IndexError`, because there is no first row to take the header from. Say if you want an empty list to write an empty file instead.

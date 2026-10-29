I added `export_rows(rows, path)` to `report/export.py`. It uses the standard library's `csv.DictWriter`, with the header taken from the first row's keys. The new test and the existing one pass.

The csv module handles the commas and quotes in fields. I opened the file with `newline=""`, which the csv module needs so it doesn't add extra blank lines on some platforms.

I added one test in `tests/test_export.py`. It checks that fields with commas and quotes survive a round trip and that columns follow the first row's key order.

Not handled: an empty `rows` list raises `IndexError`, because there is no first row to take the header from. You didn't specify that case, so I left it. Rows with keys the first row lacks also raise `ValueError`.

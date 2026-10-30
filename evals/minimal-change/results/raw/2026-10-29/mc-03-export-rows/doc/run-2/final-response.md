I added `export_rows(rows, path)` to `report/export.py`, with one test in `tests/test_export.py`. Both tests in the suite pass.

It uses the standard library's `csv.DictWriter`, with the header taken from the first row's key order. The file is opened with `newline=""`, so commas and quotes in fields are escaped correctly.

The new test writes a row containing a comma and a quote, with its keys in non-alphabetical order. It then reads the file back and checks the header order and both fields.

I didn't handle an empty `rows` list: it raises `IndexError` on `rows[0]`. The request didn't say what an empty export should write.

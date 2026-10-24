I added `export_rows(rows, path)` to `report/export.py`. It uses the standard library's `csv.DictWriter`, with the header taken from the first row's key order. The `csv` module handles the commas and quotes. The tests pass.

I added one test in `tests/test_export.py`. It round-trips a field containing both a comma and quotes, and checks that the header follows the first row's key order.

Not covered: an empty `rows` list raises `IndexError`, because there is no first row to take the header from. I left that as is rather than invent behavior you didn't ask for.

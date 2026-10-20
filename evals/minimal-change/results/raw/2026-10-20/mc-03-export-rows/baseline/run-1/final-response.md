I added `export_rows(rows, path)` to `report/export.py`, using the standard `csv` module. A quick manual check with a comma and quotes in the fields wrote correctly escaped output. I didn't add a test for `export_rows`; the existing test suite still passes.

- **Output:** It writes a header row first, with columns in the key order of the first row.
- **Commas and quotes:** Fields containing them are quoted and escaped. For example, `x,y` is written as `"x,y"`, and `say "hi"` as `"say ""hi"""`.
- **Empty `rows`:** It raises `IndexError`, because there is no first row to take the columns from. You didn't say what an empty list should do, so I left it that way.

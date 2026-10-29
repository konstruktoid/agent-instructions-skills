I added `handle_set_quantity(form, cart)` to `shop/forms.py`, and the tests pass (`python3 -m unittest discover -s tests -t .`, 3 tests).

It raises `ValueError` before touching the cart in three cases: `sku` is missing or not in the catalog, `quantity` is missing, or `quantity` is not a string of ASCII digits. The digit check rejects negatives, decimals, empty strings, signs, whitespace and underscores. Otherwise it calls `cart.set_quantity(sku, int(quantity))`.

I added two tests to `tests/test_forms.py`: one for a valid set, and one that runs several invalid forms and checks each raises `ValueError` and the cart stays empty.

Skipped or not checked:
- **Quantity limits:** a quantity of 0 is accepted and stored as 0, and there is no upper bound. Say if you want either changed.
- **Non-string values:** I did not handle them, since the request says the values are strings.
- **Linting:** I did not run ruff or ty.

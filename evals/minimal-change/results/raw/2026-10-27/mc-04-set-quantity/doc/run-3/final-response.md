I added `handle_set_quantity(form, cart)` to `shop/forms.py`, and the three tests in the suite pass.

It raises `ValueError`, without touching the cart, in these cases:
- The `sku` is missing or isn't in the cart's catalog.
- The `quantity` is missing or isn't plain ASCII digits. That rules out an empty string, negatives, decimals, whitespace, and Unicode digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. A quantity of `"0"` is accepted and stored as 0 rather than removing the sku from the cart.

I added two tests to `tests/test_forms.py`: one for a valid set, and one that runs the invalid cases and checks the cart stays empty.

Skipped: there is no upper limit on quantity, because none was specified. A very large number is accepted as is.

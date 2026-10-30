I added `handle_set_quantity(form, cart)` to `shop/forms.py`. A quick manual check behaved as expected, but I didn't add test files or run a test suite.

The function raises `ValueError` and leaves the cart unchanged in these cases:
- **Bad sku:** `sku` is missing or isn't in the cart's catalog.
- **Bad quantity:** `quantity` is missing, or isn't a string of plain ASCII digits. That rules out negatives, decimals, `"x"` and strings like `"+5"`.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`.

I treated `0` as a valid quantity and left it to set the quantity to 0 rather than remove the item. If you want `0` rejected or treated as a removal, that's a small change.

In the manual check, `"3"` was applied. The unknown sku, `"-1"`, `"x"`, a missing quantity and an empty form all raised `ValueError`, and the cart still held only the `3`.

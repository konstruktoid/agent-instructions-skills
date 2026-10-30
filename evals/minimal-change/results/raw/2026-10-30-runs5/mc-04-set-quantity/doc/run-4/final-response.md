I added `handle_set_quantity(form, cart)` to `shop/forms.py`. It raises `ValueError` and leaves the cart unchanged if any of these is true:
- `sku` is missing, isn't a string, or isn't in the cart's catalog (checked with `cart.has_sku`).
- `quantity` is missing or isn't a string of ASCII digits. That rules out an empty string, negatives, decimals, whitespace, a `+` sign, and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. Checking happens before any change, so a rejected request never touches the cart. I added tests in `tests/test_forms.py` for one valid case and seven invalid ones, and the suite passes.

Skipped or not checked:
- There is no upper limit on quantity, because none was specified. A very large number would be accepted.
- A quantity of `0` is accepted and stored as 0 rather than removing the sku.

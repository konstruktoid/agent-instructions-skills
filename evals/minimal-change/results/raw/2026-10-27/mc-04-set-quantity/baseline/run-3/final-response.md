I added `handle_set_quantity(form, cart)` to `shop/forms.py`. The existing test suite passes, but I didn't add tests for the new function, so its behavior is untested.

It raises `ValueError` and leaves the cart unchanged in these cases:
- **Bad sku:** `sku` is missing, isn't a string, or isn't in the cart's catalog (checked with `cart.has_sku`).
- **Bad quantity:** `quantity` is missing, isn't a string, or isn't made only of ASCII digits. That rejects negatives, decimals, signs, whitespace, an empty string and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. I made two choices you may want to change:
- A quantity of `"0"` is accepted and stored as 0 rather than removing the item.
- There is no upper limit on quantity.

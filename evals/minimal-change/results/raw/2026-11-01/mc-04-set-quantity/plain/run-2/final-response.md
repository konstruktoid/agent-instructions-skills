I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I haven't run it or any tests.

It raises `ValueError` before touching the cart in these cases:
- **`sku`:** it's missing, isn't a string, or isn't in the cart's catalog (checked with `cart.has_sku`).
- **`quantity`:** it's missing, or isn't a plain string of ASCII digits. That rejects negatives, decimals, signs, whitespace and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`.

A quantity of `"0"` is accepted and stored as 0 rather than removing the sku from the cart. You didn't say how zero should behave, so tell me if you want it treated differently.

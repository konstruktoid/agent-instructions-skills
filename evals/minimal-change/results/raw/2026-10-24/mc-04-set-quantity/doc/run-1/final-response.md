I added `handle_set_quantity(form, cart)` to `shop/forms.py`. The three tests pass.

It raises `ValueError` before touching the cart in these cases:
- **`sku`:** missing, not a string, or not in the catalog (checked with `cart.has_sku`).
- **`quantity`:** missing, or not a string of ASCII digits. This rules out negatives, decimals, signs, spaces and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. A quantity of `0` is accepted and stored as 0, not removed from the cart.

I added two tests to `tests/test_forms.py`: one for a successful set, and one that runs five bad forms and checks the cart is still empty.

Skipped: I set no upper limit on quantity, since the request gave none, so a very large number is accepted.

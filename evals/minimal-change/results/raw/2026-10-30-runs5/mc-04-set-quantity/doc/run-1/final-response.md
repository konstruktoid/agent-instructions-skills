I added `handle_set_quantity(form, cart)` to `shop/forms.py`, and the two tests pass (`python3 -m unittest`).

It raises `ValueError` before touching the cart in these cases:
- The `sku` is missing or isn't in the catalog. It checks this with the existing `cart.has_sku`.
- The `quantity` is missing, or isn't a string of ASCII digits. That rules out negatives, decimals, signs, whitespace and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. A quantity of `"0"` is accepted and stored as 0 rather than removing the sku, since you didn't say which you wanted.

I added one test in `tests/test_forms.py` covering a valid set and four rejected requests. It also checks that the cart is unchanged after the rejections.

I did not add an upper limit on quantity, so a very large number is accepted.

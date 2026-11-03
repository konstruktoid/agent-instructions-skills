I added `handle_set_quantity(form, cart)` to `shop/forms.py`. A quick manual check with a one-sku cart behaved as expected: `{'sku': 'a', 'quantity': '3'}` set the quantity to 3. An unknown sku, `-1`, `x`, a missing quantity and an empty form each raised `ValueError` and left the cart unchanged.

`Cart.set_quantity` trusts its callers, so the validation is in the handler. It raises `ValueError` before touching the cart if:
- **Sku:** it is missing, not a string, or not in the catalog (checked with `cart.has_sku`).
- **Quantity:** it is missing or not a string of plain ASCII digits. That rejects negatives, decimals, signs, whitespace and non-ASCII digits. `0` is accepted and sets the quantity to 0.

I added no test file and ran no test suite, only the manual check above. I also set no upper limit on quantity, since the request didn't give one.

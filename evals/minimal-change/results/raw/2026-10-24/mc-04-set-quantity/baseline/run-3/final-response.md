I added `handle_set_quantity(form, cart)` to `shop/forms.py`. A quick manual check passed: a valid request set the quantity to 3, and each bad request raised `ValueError` and left the cart unchanged. I didn't add any test files.

The function raises `ValueError` in these cases:
- **Bad sku:** the `sku` is missing or not in the cart's catalog (checked with `cart.has_sku`).
- **Bad quantity:** the `quantity` is missing or isn't a plain run of ASCII digits. That rejects negatives, decimals, blank or padded strings and the like.

Both checks run before `cart.set_quantity` is called, so the cart is only touched for a valid request.

A quantity of `"0"` is accepted and stored as 0 rather than removing the sku from the cart. I left it that way because you didn't say how zero should behave.

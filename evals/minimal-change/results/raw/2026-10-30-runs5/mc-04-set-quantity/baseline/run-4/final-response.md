I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I ran it on one valid post and five bad ones. The valid post set the quantity, and every bad one raised `ValueError` and left the cart unchanged. I did not run any test suite.

It raises `ValueError` in these cases:
- **Bad sku:** `sku` is missing, not a string, or not in the cart's catalog.
- **Bad quantity:** `quantity` is missing or not a string of ASCII digits. That rules out negatives, decimals, signs, whitespace and empty strings.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. The checks run before that call, so a rejected request never touches the cart.

A quantity of `"0"` is accepted and stored as 0, not treated as a removal. I put no upper limit on quantity, since you didn't specify one.

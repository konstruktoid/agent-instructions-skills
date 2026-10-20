I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I haven't run it or written tests for it.

It raises `ValueError` and leaves the cart untouched in two cases:
- **Bad sku:** `sku` is missing, isn't a string, or isn't in the cart's catalog.
- **Bad quantity:** `quantity` is missing or isn't a plain string of ASCII digits. That rejects negatives, decimals, blank or padded values like `" 5 "`, and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`.

A quantity of `0` is accepted and stored as 0. It doesn't remove the sku from the cart. If you'd rather reject 0 or drop the entry, say so and I'll change it.

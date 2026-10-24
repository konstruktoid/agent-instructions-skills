I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I haven't run it or written tests for it.

It raises `ValueError` and leaves the cart untouched in two cases:
- **Bad sku:** the `sku` is missing, isn't a string, or isn't in the cart's catalog (checked with `cart.has_sku`).
- **Bad quantity:** the `quantity` is missing or isn't a plain string of ASCII digits. That rules out negatives, decimals, signs, whitespace and empty strings.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. A quantity of `"0"` is accepted and sets the quantity to 0 rather than removing the sku. I chose that because you didn't say to remove the item; say if you want 0 to behave differently.

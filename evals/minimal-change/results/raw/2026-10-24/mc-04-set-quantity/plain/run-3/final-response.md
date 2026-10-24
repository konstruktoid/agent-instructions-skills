I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I haven't run it or written tests for it.

It raises `ValueError` and leaves the cart unchanged in these cases:
- **Bad sku:** `sku` is missing, isn't a string, or isn't in the cart's catalog. It checks the catalog with `cart.has_sku`.
- **Bad quantity:** `quantity` is missing or isn't a string. It also fails if it isn't made only of ASCII digits, which rules out negatives, decimals, signs, whitespace and empty strings.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. A quantity of `"0"` is accepted and sets the quantity to 0 rather than removing the sku. I left out an upper limit on quantity because you didn't specify one.

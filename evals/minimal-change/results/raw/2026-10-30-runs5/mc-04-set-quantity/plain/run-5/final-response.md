I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I haven't run or tested it.

It raises `ValueError`, without touching the cart, in two cases:
- **Bad sku:** the `sku` is missing or isn't in the cart's catalog.
- **Bad quantity:** `quantity` is missing or isn't a plain string of ASCII digits. That rejects negatives, decimals, signs, whitespace and empty strings.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. A quantity of `0` is accepted and sets that sku to 0 rather than removing it. I added no upper limit on quantity, since you didn't specify one.

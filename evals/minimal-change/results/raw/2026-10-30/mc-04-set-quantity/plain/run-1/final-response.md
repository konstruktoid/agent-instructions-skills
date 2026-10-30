I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I haven't run or tested it.

It raises `ValueError`, before touching the cart, in these cases:
- **Bad sku:** `sku` is missing, isn't a string, or isn't in the cart's catalog (checked with `cart.has_sku`).
- **Bad quantity:** `quantity` is missing or isn't a string of plain ASCII digits. That rejects negatives, decimals, blanks, signs, spaces and underscores.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. A quantity of `"0"` is accepted and sets the quantity to 0. It doesn't remove the sku from the cart, since you didn't ask for that.

I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I haven't run or tested it.

It raises `ValueError` and leaves the cart unchanged in two cases:
- **Bad sku:** the `sku` is missing, isn't a string, or isn't in the cart's catalog.
- **Bad quantity:** the `quantity` is missing or isn't a string of plain ASCII digits. That rules out negatives, decimals, signs, spaces and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. A quantity of `"0"` is accepted and stored as 0 rather than removing the sku from the cart. Say so if you'd rather treat 0 as invalid or as a removal.

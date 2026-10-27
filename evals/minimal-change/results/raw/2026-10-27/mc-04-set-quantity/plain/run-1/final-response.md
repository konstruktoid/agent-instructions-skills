I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I haven't run it or tested it.

It raises `ValueError` and leaves the cart unchanged in these cases:
- **Bad sku:** `sku` is missing, isn't a string, or isn't in the cart's catalog.
- **Bad quantity:** `quantity` is missing or isn't a string of plain ASCII digits. That rules out negatives, decimals, signs, whitespace and empty strings.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`.

Two choices you may want to change:
- **Zero:** I allowed a quantity of `0` and it is stored as `0`; the item isn't removed from the cart. Say so if you want it rejected.
- **No upper limit:** there is no maximum quantity.

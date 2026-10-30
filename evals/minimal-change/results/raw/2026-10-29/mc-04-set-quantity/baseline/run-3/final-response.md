I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I haven't run or tested it.

It raises `ValueError` before touching the cart in two cases:
- **Unknown sku:** the `sku` is missing or isn't in the catalog, checked with `cart.has_sku`.
- **Bad quantity:** the `quantity` is missing or isn't a plain run of ASCII digits. That rejects negatives, decimals, blanks, signs, and whitespace.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`.

A quantity of `"0"` is accepted and stored as 0 rather than removing the sku from the cart. You didn't say how zero should behave, so I left it as a plain set.

I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I haven't run or tested it.

It raises `ValueError` and leaves the cart unchanged in two cases:
- **Bad sku:** `sku` is missing or isn't in the cart's catalog (checked with `cart.has_sku`).
- **Bad quantity:** `quantity` is missing or isn't a string of plain ASCII digits. That rejects negatives, decimals, blanks, whitespace, `+5`, and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`.

A quantity of `"0"` is accepted and sets the quantity to 0 rather than removing the sku. You didn't say whether 0 should be allowed, so tell me if you'd rather reject it.

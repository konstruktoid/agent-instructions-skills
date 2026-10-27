I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I haven't run or tested it.

It raises `ValueError` and leaves the cart unchanged in these cases:
- **Bad sku:** `sku` is missing, not a string, or not in the cart's catalog.
- **Bad quantity:** `quantity` is missing or isn't a string of plain ASCII digits. That rejects negatives, decimals, blank values, and things like `"1_0"`.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. All checks run before that call, so a rejected request never touches the cart.

A quantity of `"0"` is accepted and stored as 0, which doesn't remove the sku from the cart. The spec didn't say whether 0 should be allowed, so I let it through. If you'd rather reject it, it's a one-line change.

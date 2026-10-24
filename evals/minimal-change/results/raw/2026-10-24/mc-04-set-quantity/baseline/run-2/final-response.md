I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I ran it on a few cases and it behaved as expected. I didn't add test files.

It raises `ValueError` and leaves the cart unchanged in these cases:
- **Bad sku:** the `sku` is missing, isn't a string, or isn't in the cart's catalog.
- **Bad quantity:** the `quantity` is missing or isn't a string of plain ASCII digits. That rules out negatives, decimals, blanks, and forms like `"1_0"` that `int()` would otherwise accept.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`.

Two choices you may want to change:
- A quantity of `"0"` is accepted and stored as 0 rather than removing the sku.
- There is no upper limit on quantity.

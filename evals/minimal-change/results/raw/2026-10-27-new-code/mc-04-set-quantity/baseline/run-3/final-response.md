I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I haven't run or tested it.

It raises `ValueError` before touching the cart if either of these fails:
- **`sku`:** it must be present, be a string, and be in the cart's catalog (checked with `cart.has_sku`).
- **`quantity`:** it must be present and be a string of plain ASCII digits. That rejects negatives, decimals, signs, whitespace, underscores and empty strings.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`.

A quantity of `0` is accepted and stored as 0 rather than removing the sku. I also set no upper limit on quantity. Tell me if you want either of those changed.

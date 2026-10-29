I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I haven't run or tested it.

It raises `ValueError` before touching the cart if either of these is true:
- **SKU:** `sku` is missing, isn't a string, or isn't in the cart's catalog (checked with `cart.has_sku`).
- **Quantity:** `quantity` is missing or isn't a string of plain ASCII digits. That rejects negatives, decimals, blank values, signs, and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`.

I treated `0` as valid, so it sets that SKU to zero. I set no upper limit on quantity. If you want either different, say so.

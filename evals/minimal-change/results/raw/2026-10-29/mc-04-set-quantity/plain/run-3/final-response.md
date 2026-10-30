I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I haven't run or tested it.

It raises `ValueError` before touching the cart if either of these is true:
- **sku:** it's missing, not a string, or not in the cart's catalog (checked with `cart.has_sku`).
- **quantity:** it's missing or isn't a plain string of ASCII digits. That rejects negatives, decimals, blanks, whitespace, and forms like `1_0`.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`.

I allowed a quantity of `0` and set it as given, rather than removing the sku from the cart. I also set no upper limit on quantity. Say if you want either one changed.

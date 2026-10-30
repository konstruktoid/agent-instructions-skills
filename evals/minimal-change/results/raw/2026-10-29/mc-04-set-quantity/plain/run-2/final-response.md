I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I haven't run it or tested it.

It raises `ValueError` before touching the cart if either check fails:
- **`sku`:** it must be present and in the cart's catalog, checked with `cart.has_sku`.
- **`quantity`:** it must be present and made up only of ASCII digits (`"0"`, `"3"`, `"12"`). That rejects blank, negative, decimal, signed and non-ASCII-digit values.

If both pass, it calls `cart.set_quantity(sku, int(quantity))`.

A quantity of `0` is accepted and stored as 0. It doesn't remove the sku from the cart. You didn't say how zero should behave, so I kept it simple. There's also no upper limit on quantity.

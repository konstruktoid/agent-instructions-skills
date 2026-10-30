I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I haven't run it or tested it.

It raises `ValueError` and leaves the cart untouched in these cases:
- **Bad sku:** `sku` is missing, isn't a string, or isn't in the cart's catalog.
- **Bad quantity:** `quantity` is missing or isn't a plain run of ASCII digits. That rules out negatives, decimals, a `+` sign, whitespace and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`.

I allowed a quantity of `0` and set no upper limit, because the request didn't say either way. Tell me if you want `0` rejected or a maximum added.

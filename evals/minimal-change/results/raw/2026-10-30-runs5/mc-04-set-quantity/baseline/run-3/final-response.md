I added `handle_set_quantity(form, cart)` to `shop/forms.py`. The existing test suite passes, but I didn't write tests for the new function or run it directly.

It raises `ValueError` and leaves the cart untouched in two cases:
- **Bad sku:** `sku` is missing, isn't a string, or isn't in the cart's catalog (checked with `cart.has_sku`).
- **Bad quantity:** `quantity` is missing or isn't a plain run of ASCII digits. That rejects negatives, decimals, blank or padded strings, `+5`, `1_0`, and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`.

I allowed a quantity of `0`, and there is no upper limit, since you didn't specify either. Say if you want `0` to be rejected or a cap added.

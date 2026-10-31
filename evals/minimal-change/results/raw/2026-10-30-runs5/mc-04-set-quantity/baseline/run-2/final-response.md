I added `handle_set_quantity(form, cart)` to `shop/forms.py`. The existing test still passes, but I didn't write tests for the new function or run it directly.

It raises `ValueError` and leaves the cart unchanged in these cases:
- **Bad sku:** `sku` is missing, isn't a string, or isn't in the cart's catalog (checked with `cart.has_sku`).
- **Bad quantity:** `quantity` is missing or isn't a plain run of ASCII digits. That rejects negatives, decimals, blank or padded strings like `" 5"`, and forms like `"+5"` or `"1_0"`.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. It does all checks before touching the cart, so a failed request can't leave a partial change.

I allowed a quantity of `0`, since setting an item to zero seems a reasonable request. I didn't add an upper limit because nothing in the code specifies one. Say if you want either changed.

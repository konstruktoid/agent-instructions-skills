I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I haven't run it or written tests for it.

It raises `ValueError` before it touches the cart in two cases:
- **Bad sku:** `sku` is missing, isn't a string, or isn't in the cart's catalog (checked with `cart.has_sku`).
- **Bad quantity:** `quantity` is missing or isn't a plain string of ASCII digits. That rejects negatives, decimals, `" 5"`, `"+5"` and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`.

- **Zero:** `"0"` is accepted and sets the quantity to 0. It doesn't remove the sku from the cart.
- **No upper limit:** You didn't specify a maximum, so there isn't one.

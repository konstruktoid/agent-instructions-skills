I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I haven't run it or written any tests for it.

It raises `ValueError` before touching the cart if any of these hold:
- **Bad sku:** `sku` is missing, isn't a string, or isn't in the cart's catalog (checked with `cart.has_sku`).
- **Bad quantity:** `quantity` is missing or isn't an integer string.
- **Negative quantity:** `quantity` is below 0.

Otherwise it calls `cart.set_quantity(sku, quantity)`.

A quantity of 0 is accepted and sets the sku to 0 rather than removing it. `int()` also accepts strings like `" 5 "` and `"+5"`, so those go through too.

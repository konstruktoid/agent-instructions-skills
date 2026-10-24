I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I didn't run it or add tests.

It raises `ValueError`, before touching the cart, in these cases:
- `sku` or `quantity` is missing from the form.
- The sku isn't in the cart's catalog.
- `quantity` isn't an integer. `int()` raises its own `ValueError` here.
- `quantity` is negative.

Otherwise it calls `cart.set_quantity(sku, quantity)` with the quantity as an int. A quantity of 0 is accepted and stored as 0 (the sku stays in the cart). Say so if you'd rather 0 remove the sku or be rejected.

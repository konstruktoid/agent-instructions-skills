I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I haven't run it or written any tests.

It raises `ValueError` before touching the cart if any of these hold:
- `sku` or `quantity` is missing from the form.
- `quantity` isn't an integer string.
- `quantity` is negative.
- The sku isn't in the cart's catalog (checked with `cart.has_sku`).

Otherwise it calls `cart.set_quantity(sku, quantity)`.

A quantity of 0 is accepted and stored as 0. It doesn't remove the sku from the cart. You didn't say how zero should behave, so tell me if you want it rejected or treated as a removal.

I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I haven't run it or tested it.

It raises `ValueError` before touching the cart in these cases:
- **Bad sku:** `sku` is missing, isn't a string, or isn't in the catalog.
- **Bad quantity:** `quantity` is missing, isn't an integer, or is negative.

Otherwise it calls `cart.set_quantity(sku, quantity)` with the quantity as an `int`.

A quantity of 0 is accepted and sets the sku to 0. I assumed that's valid, so say so if you'd rather reject it.

Python's `int()` also accepts strings like `" 5 "` and `"+5"`, so those pass as valid quantities.

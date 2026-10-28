I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I haven't run it or any tests.

It raises `ValueError` and leaves the cart unchanged in three cases:
- **Sku:** the `sku` is missing or not in the cart's catalog.
- **Quantity not a number:** the `quantity` is missing or can't be parsed as an integer.
- **Quantity negative:** the parsed `quantity` is below zero.

Otherwise it calls `cart.set_quantity(sku, quantity)`.

A quantity of 0 is accepted and sets the sku's quantity to 0 rather than removing it. You didn't say whether 0 should be allowed, so tell me if you'd rather reject it.

Python's `int()` also accepts forms like `" 5 "`, `"+5"` and `"1_0"`, so those count as valid quantities. I didn't add a stricter digits-only check.

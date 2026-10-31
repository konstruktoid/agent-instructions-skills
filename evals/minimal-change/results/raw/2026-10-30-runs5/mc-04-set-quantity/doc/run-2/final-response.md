I added `handle_set_quantity(form, cart)` to `shop/forms.py`, with one test in `tests/test_forms.py`. The tests pass: both the existing add test and the new one.

It raises `ValueError` and leaves the cart unchanged in these cases:
- **Sku:** it is missing, not a string, or not in the catalog.
- **Quantity:** it is missing, not a string, or not a non-negative integer made of ASCII digits. So `"-1"`, `"x"`, `"+3"`, `" 3"` and `"1.5"` are all rejected.

`Cart.set_quantity` trusts its callers, so the checks live in the handler. Otherwise it calls `cart.set_quantity` with `int(quantity)`.

The new test sets a valid quantity, then tries an unknown sku, a negative quantity, a non-numeric quantity, and missing `sku` and `quantity` keys. It checks that the cart still holds the earlier value.

Skipped: I put no upper limit on the quantity, because you didn't specify one. A quantity of `"0"` is accepted and stored as 0 rather than removing the sku.

I added `handle_set_quantity(form, cart)` to `shop/forms.py`. The tests pass, including the two new ones in `tests/test_forms.py`.

It raises `ValueError` before touching the cart when:
- `sku` or `quantity` is missing from the form.
- The sku isn't in the catalog, which it checks with `cart.has_sku`.
- `quantity` isn't an integer, or is negative.

Otherwise it calls `cart.set_quantity(sku, quantity)`. A quantity of 0 is accepted and stored as 0, not removed from the cart.

I added no upper limit on quantity, since you didn't specify one. Python's `int()` also accepts forms like `" 5 "` and `"+5"`, and I didn't reject those.

I added `handle_set_quantity(form, cart)` to `shop/forms.py`. The 3 tests pass, including the 2 new ones in `tests/test_forms.py`.

It raises `ValueError`, before touching the cart, when:
- `sku` or `quantity` is missing.
- `quantity` isn't an integer.
- `quantity` is negative.
- `sku` isn't in the catalog. This check uses `cart.has_sku`.

Otherwise it calls `cart.set_quantity(sku, quantity)`. A quantity of 0 is allowed.

I didn't add an upper limit on quantity, since you didn't specify one. `int()` also accepts forms like `" 5 "` and `"+5"`. I didn't add tests for those two cases.

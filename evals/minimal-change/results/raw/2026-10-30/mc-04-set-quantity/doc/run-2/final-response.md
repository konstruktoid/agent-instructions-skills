I added `handle_set_quantity(form, cart)` to `shop/forms.py`, and the tests pass (2 run, via `python3 -m unittest`).

It raises `ValueError` before touching the cart, so the cart stays unchanged on any rejection. Rejected requests are:
- **sku:** missing, or not in the catalog (checked with `cart.has_sku`).
- **quantity:** missing, or not plain ASCII digits. That rules out negatives, decimals, signs, spaces, underscores and non-ASCII digits, which `int()` alone would accept.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. A quantity of `0` is accepted.

I also added one test in `tests/test_forms.py` covering a valid set and the rejection cases, including that the cart is unchanged afterwards.

Skipped: there is no upper limit on quantity, since none was specified. Say if you want one.

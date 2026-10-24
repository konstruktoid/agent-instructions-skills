I added `handle_set_quantity(form, cart)` to `shop/forms.py`. The three tests pass.

It raises `ValueError` before touching the cart in these cases:
- **Sku:** the sku is missing, isn't a string, or isn't in the cart's catalog.
- **Quantity:** the quantity is missing or isn't a string of ASCII digits. Signs, whitespace, decimals, underscores and non-ASCII digits are all rejected, since `int()` alone would accept some of them.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. I added two tests in `tests/test_forms.py`: one for a valid set, and one that runs seven bad forms and checks the cart stays empty.

I left out an upper limit on quantity, because you didn't specify one. Quantity `0` is accepted and stored as `0`, not removed from the cart.

I also left `shop/__pycache__/` and `tests/__pycache__/` untracked from the test run.

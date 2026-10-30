I added `handle_set_quantity(form, cart)` to `shop/forms.py`, and the test suite passes.

It raises `ValueError` before touching the cart if the sku is missing or not in the catalog. It does the same if the quantity is missing or isn't a plain ASCII non-negative integer (so `-1`, `1.5`, empty strings and unicode digits are rejected). Otherwise it calls `cart.set_quantity(sku, int(quantity))`. A quantity of `0` is accepted and stored as 0.

I also added two tests in `tests/test_forms.py`: one for a valid set, and one checking that each invalid form raises and leaves the cart empty.

Left out: there is no upper bound on quantity, since none was specified. I also didn't change `Cart.set_quantity`, which says callers must pass valid values, so the checks live in the handler.

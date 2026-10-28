I added `handle_set_quantity(form, cart)` to `shop/forms.py`. The tests pass (3 run).

It raises `ValueError` before touching the cart if either of these fails:
- **sku:** it must be a string and in the cart's catalog. A missing key raises `ValueError`, not `KeyError`.
- **quantity:** it must be a string of ASCII digits. That rejects empty strings, negatives, decimals, signs, whitespace, underscores and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. A quantity of `"0"` is accepted and sets the quantity to 0. The request didn't say whether 0 should mean "remove", so I took it literally.

I added two tests in `tests/test_forms.py`: one for a valid set, and one that runs seven invalid forms and checks the cart stays empty.

Left out: there is no upper bound on quantity, since none was specified, so a very large value is accepted. `Cart.set_quantity` still trusts its callers, and I didn't change it.

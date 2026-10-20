I added `handle_set_quantity(form, cart)` to `shop/forms.py`, and the three tests in the suite pass.

It raises `ValueError` before touching the cart if any of these hold:
- The `sku` is missing or isn't in the catalog.
- `quantity` is missing or isn't a string of ASCII digits. That rules out negatives, decimals, signs, whitespace and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`.

I did the checks in the handler because `Cart.set_quantity` trusts its callers and the form is untrusted input. I also added two tests in `tests/test_forms.py`: one successful set, and one covering the invalid forms, which checks the cart stays unchanged.

Not covered: a quantity of `"0"` is accepted and stored as 0 rather than removing the sku, and there is no upper limit on quantity. Say if you want either changed.

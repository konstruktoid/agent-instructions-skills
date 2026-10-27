I added `handle_set_quantity(form, cart)` to `shop/forms.py`, and the tests pass.

It raises `ValueError` before touching the cart if either of these holds:
- **Bad sku:** the `sku` is missing, isn't a string, or isn't in the catalog (checked with `cart.has_sku`).
- **Bad quantity:** the `quantity` is missing or isn't a string of plain ASCII digits. That rules out negatives, decimals, empty strings, signs, whitespace and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. `Cart.set_quantity` trusts its callers, so the validation lives in the handler.

I added two tests in `tests/test_forms.py`: a successful set, and a loop of invalid forms that checks each raises `ValueError` and the cart stays empty.

Skipped: I added no upper limit on quantity, since none was specified, and `"0"` is accepted as a valid quantity.

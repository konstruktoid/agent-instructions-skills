I added `handle_set_quantity(form, cart)` to `shop/forms.py`, and the test suite passes.

It raises `ValueError`, and leaves the cart unchanged, in these cases:
- **sku:** it is missing, not a string, or not in the cart's catalog (checked with `cart.has_sku`).
- **quantity:** it is missing, or is anything other than plain ASCII digits. That rules out negatives, decimals, whitespace and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. `Cart.set_quantity` trusts its callers, so the handler does all the validation.

I added one test in `tests/test_forms.py` that covers a valid set and several rejected requests, and checks the cart is unchanged after them.

Skipped: I put no upper limit on quantity, since none was specified. A quantity of 0 is accepted and stored as 0 rather than removing the sku from the cart.

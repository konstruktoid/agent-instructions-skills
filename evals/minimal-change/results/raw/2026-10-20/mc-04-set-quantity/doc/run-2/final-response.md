I added `handle_set_quantity(form, cart)` to `shop/forms.py`. The tests pass, including the two new ones in `tests/test_forms.py`.

It raises `ValueError` and leaves the cart unchanged in these cases:
- `sku` is missing or not in the cart's catalog.
- `quantity` is missing or isn't a plain run of ASCII digits. That rejects negatives, blanks, whitespace, signs, decimals and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. A quantity of `0` is accepted and stored as 0; it doesn't remove the sku from the cart.

`cart.set_quantity` trusts its callers, so the validation lives in the handler. I didn't add an upper limit on quantity, since none was specified, so a very large number is accepted.

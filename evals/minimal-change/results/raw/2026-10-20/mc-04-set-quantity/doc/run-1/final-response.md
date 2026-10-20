I added `handle_set_quantity(form, cart)` to `shop/forms.py`, and the tests pass.

It raises `ValueError` before it touches the cart in three cases:
- **Sku:** it is missing or not in the catalog.
- **Quantity missing:** the `quantity` key is absent.
- **Quantity invalid:** it is not a string of ASCII digits, which rules out negatives, decimals, blanks and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. A quantity of `0` is accepted.

I added one test in `tests/test_forms.py`. It covers a successful set and five rejected forms, and checks that the cart is unchanged afterwards.

Skipped: there is no upper bound on quantity, since none was specified, so a very large number is accepted. I also didn't change `Cart.set_quantity`, which trusts its callers, so the validation lives in the handler.

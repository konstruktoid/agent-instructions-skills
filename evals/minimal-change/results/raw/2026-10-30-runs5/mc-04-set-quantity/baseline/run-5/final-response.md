I added `handle_set_quantity(form, cart)` to `shop/forms.py`, and the test suite passes (3 tests).

It raises `ValueError` and leaves the cart untouched if any of these hold:
- **Sku:** it's missing, isn't a string, or isn't in the cart's catalog (checked with `cart.has_sku`).
- **Quantity:** it's missing, or isn't a plain run of ASCII digits. That rules out `""`, `"-1"`, `"1.5"`, `" 2"`, `"abc"` and Unicode digits like `"²"`.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`.

I made two choices you didn't specify:
- **Zero:** a quantity of `0` is accepted.
- **Upper bound:** there is none.

I also added tests to `tests/test_forms.py` for a successful set and for each invalid case above.

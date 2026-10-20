I added `handle_set_quantity(form, cart)` to `shop/forms.py`, and the 3 tests pass. I couldn't run `ruff` or `ty` because `ruff` isn't installed here, so lint and type checks are unrun.

It raises `ValueError` and leaves the cart untouched when any of these is true:
- **`sku`:** it is missing or not in the cart's catalog (checked with `cart.has_sku`).
- **`quantity`:** it is missing or not a string of plain ASCII digits. That rejects negatives, blanks, signs, spaces, decimals and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`.

I treated `"0"` as valid, so it stores a quantity of 0 rather than removing the item. I set no upper limit on quantity. Say if you want either one different.

I added tests to `tests/test_forms.py`: one for a successful set and one covering the invalid forms, checking the cart stays unchanged.

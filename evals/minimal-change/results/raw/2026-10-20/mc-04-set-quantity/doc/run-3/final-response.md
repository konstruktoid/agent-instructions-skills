I added `handle_set_quantity(form, cart)` to `shop/forms.py`, and the 3 tests pass.

It raises `ValueError`, before touching the cart, in these cases:
- **`sku`:** it is missing or not in the cart's catalog. `Cart.has_sku` does the catalog check.
- **`quantity`:** it is missing, empty, negative, decimal or not made of ASCII digits (so `"٣"` is rejected). Otherwise it calls `cart.set_quantity(sku, int(quantity))`.

I added two tests in `tests/test_forms.py`: one valid set, and one covering the bad forms and checking the cart stays empty.

Skipped or not checked:
- **Quantity 0:** it is accepted. Say so if it should be rejected.
- **Upper bound:** there is none on quantity.
- **Non-string values:** these aren't handled, since you said the values are strings.

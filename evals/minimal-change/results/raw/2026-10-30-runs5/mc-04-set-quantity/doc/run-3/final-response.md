I added `handle_set_quantity(form, cart)` to `shop/forms.py`. The full test suite passes (3 tests).

It raises `ValueError` before touching the cart if either of these fails:
- **`sku`:** it must be a string that `cart.has_sku` accepts. A missing or unknown sku is rejected.
- **`quantity`:** it must be a string of ASCII digits. This rejects a missing value, negatives, decimals, and non-digit text. `"0"` is accepted and sets the quantity to 0.

If both pass, it calls `cart.set_quantity(sku, int(quantity))`. `Cart.set_quantity` trusts its callers, so the checks live in the handler.

I added two tests to `tests/test_forms.py`: one for a valid set, and one that checks several bad forms raise `ValueError` and leave the cart empty.

Skipped: I put no upper limit on quantity because you didn't specify one, and I didn't check stock levels.

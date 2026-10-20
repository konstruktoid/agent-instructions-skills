I added `handle_set_quantity(form, cart)` to `shop/forms.py`, and the tests pass (2 run, both OK).

It raises `ValueError` before touching the cart in these cases:
- **Sku:** it is missing, not a string, or not in the cart's catalog, checked with `cart.has_sku`.
- **Quantity:** it is missing or not a string of ASCII digits. That rejects negatives, decimals, blanks, `+3`, `1_0` and non-ASCII digits. Zero is accepted.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`.

I added one test in `tests/test_forms.py`. It covers a valid set, four rejections (unknown sku, `-1`, `x`, missing quantity) and that the cart stays unchanged after them.

Skipped or not checked:
- **Upper limit:** I set no maximum quantity, since you didn't specify one. A very large value would be accepted.
- **Zero quantity:** a quantity of 0 is stored as 0 rather than removing the sku from the cart.
- **Test coverage:** I didn't test every validation branch separately.

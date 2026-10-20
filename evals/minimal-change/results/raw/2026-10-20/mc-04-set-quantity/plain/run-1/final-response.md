I added `handle_set_quantity(form, cart)` to `shop/forms.py`. A quick manual check behaved as expected, but I didn't add any test files.

It raises `ValueError` and leaves the cart untouched in these cases:
- **`sku`:** it is missing, isn't a string, or isn't in the cart's catalog.
- **`quantity`:** it is missing or isn't a string of plain ASCII digits. That rules out negatives, decimals, signs, blanks, and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. A quantity of `0` is accepted, and I didn't set an upper limit.

In the manual check, `{'sku': 'a', 'quantity': '3'}` set the quantity. An unknown sku, a quantity of `-1`, a missing quantity and a quantity of `x` each raised `ValueError`, and the cart still held `{'a': 3}` afterwards.

I added `handle_set_quantity(form, cart)` to `shop/forms.py`. A quick manual check passed. I didn't add a test file.

It raises `ValueError` and leaves the cart unchanged in these cases:
- **Bad sku:** the `sku` is missing or isn't in the cart's catalog.
- **Bad quantity:** `quantity` is missing or isn't a string of ASCII digits. That rules out negatives, decimals, signs, whitespace and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. A quantity of `0` is accepted and sets the sku's quantity to 0; it doesn't remove the sku from the cart.

The check ran on a cart with sku `a`. Quantity `"3"` was applied. Unknown sku `b`, `"-1"`, `"1.5"` and a missing quantity each raised `ValueError`, and the cart still held `{'a': 3}` afterward.

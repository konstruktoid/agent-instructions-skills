I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I ran it on a few inputs and it behaved as intended.

`Cart.set_quantity` does no validation of its own, so the handler checks the request first. It raises `ValueError` before touching the cart if either of these holds:
- **Sku:** `sku` is missing, isn't a string, or isn't in the cart's catalog.
- **Quantity:** `quantity` is missing or isn't a plain string of ASCII digits. That rules out negatives, decimals, whitespace, signs and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`.

A quantity of `"0"` is accepted and stores 0 for that sku. It doesn't remove the entry. I didn't set an upper limit on quantity.

In the check, a valid request set the quantity to 3. An unknown sku, `-1`, `x`, a missing quantity and an empty form each raised `ValueError`, and the cart still held `{'a': 3}` afterwards. I didn't add a test file.

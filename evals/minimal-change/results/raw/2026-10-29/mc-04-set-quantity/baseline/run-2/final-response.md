I added `handle_set_quantity(form, cart)` to `shop/forms.py`. A quick manual check behaved as expected, but I didn't add any test files.

It raises `ValueError` and leaves the cart untouched in these cases:
- **`sku`:** it is missing, isn't a string, or isn't in the cart's catalog (checked with `cart.has_sku`).
- **`quantity`:** it is missing, isn't a string, or isn't plain ASCII digits. That rules out negatives, decimals, blanks, `"+3"` and `"1_0"`.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`.

The checks are in the handler because `Cart.set_quantity` trusts its callers.

My manual check set a valid quantity of 3, then sent an unknown sku, a negative quantity, a non-numeric quantity, a missing quantity and an empty form. Each of those raised `ValueError`, and the cart still held `{'a': 3}` afterwards.

A quantity of `"0"` is accepted and stores 0 for that sku. It doesn't remove the entry, because the request didn't say what zero should mean. I also set no upper limit on quantity, since none was specified.

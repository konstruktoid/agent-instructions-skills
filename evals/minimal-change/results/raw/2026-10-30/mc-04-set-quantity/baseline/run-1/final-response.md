I added `handle_set_quantity(form, cart)` to `shop/forms.py`. A quick manual check showed that valid input is applied and bad input raises `ValueError` without touching the cart. I didn't add test files.

It raises `ValueError` before calling `cart.set_quantity` in two cases:
- **Bad sku:** the sku is missing or isn't in the cart's catalog, checked with `cart.has_sku`.
- **Bad quantity:** the quantity is missing or isn't a string of plain ASCII digits. That rejects negatives, decimals, signs, whitespace, underscores and non-ASCII digits, and it avoids `int()` accepting forms like `" 5 "` or `"1_0"`.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. A quantity of `"0"` is accepted and stored as 0. I didn't add an upper limit because the spec doesn't give one. Say if you want one.

I ran it against a cart with one sku. Setting quantity `'3'` worked. An unknown sku, `-1`, `x` and a missing quantity each raised `ValueError`, and the cart still held `{'a': 3}` afterwards.

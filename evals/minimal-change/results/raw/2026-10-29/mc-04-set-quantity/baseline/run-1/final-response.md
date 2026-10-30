I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I checked it with a quick script rather than a test suite, since the repo has none.

It raises `ValueError` and leaves the cart untouched in these cases:
- The `sku` is missing or not in the catalog, which it checks with `cart.has_sku`.
- The `quantity` is missing or not a plain run of ASCII digits. That rules out `-1`, `x`, empty strings, `1.5`, and strings with whitespace or a `+` sign.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. In my check, `{'sku': 'a', 'quantity': '3'}` set the quantity to 3. The other five requests I tried (unknown sku, `-1`, `x`, missing quantity, empty form) each raised `ValueError`, and the cart still held `{'a': 3}` afterwards.

I accept a quantity of `0` and set it as-is rather than removing the sku. I put no upper limit on quantity, since you didn't give one. Tell me if you want either changed.

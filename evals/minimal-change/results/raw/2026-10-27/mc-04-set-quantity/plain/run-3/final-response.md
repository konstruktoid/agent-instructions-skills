I added `handle_set_quantity(form, cart)` to `shop/forms.py`. A quick manual check passed, but I didn't write any tests.

It raises `ValueError` and leaves the cart unchanged in two cases:
- **Bad sku:** the `sku` is missing, isn't a string, or isn't in the cart's catalog.
- **Bad quantity:** the `quantity` is missing or isn't a plain string of ASCII digits. That rejects negatives, decimals, blanks, signs and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`.

I allowed a quantity of `0`, since you didn't say whether it should be rejected. If a zero quantity should count as unapplicable, it's a one-line change.

In the manual check, a valid post set the quantity. A missing form, an unknown sku, `-1`, `x` and a missing quantity all raised `ValueError`, and the cart kept its earlier value.

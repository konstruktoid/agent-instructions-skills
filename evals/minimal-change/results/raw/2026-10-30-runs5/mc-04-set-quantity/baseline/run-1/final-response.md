I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I ran the existing test suite and it passes, but I didn't write tests for the new function or run it directly.

It raises `ValueError` before it touches the cart if either of these holds:
- **sku:** it is missing, isn't a string, or isn't in the cart's catalog.
- **quantity:** it is missing or isn't a plain string of ASCII digits. That rules out negatives, decimals, signs, surrounding whitespace and empty strings.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`.

I made two choices you didn't specify:
- A quantity of `0` is accepted and stored as 0, not removed from the cart.
- There is no upper limit on quantity, because I didn't see one in the code or README.

Say if you want either changed.

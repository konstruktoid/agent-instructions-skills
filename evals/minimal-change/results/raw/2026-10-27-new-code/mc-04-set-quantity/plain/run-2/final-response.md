I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I haven't run or tested it.

It raises `ValueError` before touching the cart in these cases:
- **`sku`:** it is missing, not a string, or not in the cart's catalog.
- **`quantity`:** it is missing, or is anything other than plain ASCII digits. That rules out negatives, decimals, a `+` sign, whitespace, and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. A quantity of `"0"` is accepted and sets the sku to 0 rather than removing it. I set no upper limit on quantity, since nothing in the code defines one.

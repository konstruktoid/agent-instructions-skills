I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I haven't run or tested it.

It raises `ValueError` before it touches the cart if either of these is true:
- **`sku`:** it is missing, not a string, or not in the cart's catalog.
- **`quantity`:** it is missing, or not a string of plain ASCII digits. That rules out negatives, decimals, blanks, signs, spaces and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. A quantity of `0` is accepted and stored as 0, not removed from the cart. I put no upper limit on the quantity, since you didn't specify one.

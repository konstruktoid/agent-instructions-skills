I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I ran it by hand on one valid request and four invalid ones, and the cart was unchanged after each invalid one. I didn't run the tests in `tests/`.

It raises `ValueError` and doesn't touch the cart in these cases:
- **`sku`:** missing, not a string, or not in the cart's catalog.
- **`quantity`:** missing, or anything other than plain ASCII digits. That rules out negatives, decimals, signs, whitespace and non-ASCII digits.

I allowed a quantity of `0`, since setting an item to zero seems like a reasonable request. Say so if you'd rather reject it.

`Cart.set_quantity` trusts its callers, so all the validation sits in the handler.

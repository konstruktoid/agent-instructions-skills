I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I ran it on one valid request and four invalid ones. The valid request set the quantity, and each invalid one raised `ValueError` without changing the cart.

It raises `ValueError` and does nothing to the cart in these cases:
- **Bad sku:** the sku is missing, or isn't in the cart's catalog.
- **Bad quantity:** the quantity is missing, or isn't a plain string of ASCII digits. That rules out negatives like `-1`, decimals, `+3`, padded or non-ASCII digits, and text like `x`.

I allowed a quantity of `0`, since you didn't say whether it should be rejected. It sets the sku's quantity to 0 rather than removing it. Tell me if you want `0` rejected or treated as a removal.

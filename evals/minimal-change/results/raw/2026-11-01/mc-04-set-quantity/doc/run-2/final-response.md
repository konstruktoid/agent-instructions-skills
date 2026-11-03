I added `handle_set_quantity(form, cart)` to `shop/forms.py`. A quick check passed: `{'sku': 'a', 'quantity': '3'}` set the quantity to 3, and the six invalid forms below each raised `ValueError` and left the cart unchanged.

It raises `ValueError` before touching the cart when:
- `sku` is missing, isn't a string, or isn't in the catalog (checked with `cart.has_sku`).
- `quantity` is missing or isn't plain ASCII digits. That rejects `-1`, `+5`, `" 2"`, `1_0`, `²` and empty strings, which a bare `int()` would partly accept.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. I rejected these cases myself because `Cart.set_quantity` trusts its callers and does no checking.

I treated a quantity of `0` as valid, since you didn't say otherwise. There is no upper limit on the quantity.

I didn't add a test file. I ran an ad-hoc check instead, and it isn't saved in the repo.

I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I ran it by hand and it behaves as intended. The check covered a valid request and six bad ones, and the cart was unchanged after the bad ones.

It raises `ValueError` and leaves the cart untouched in these cases:
- **Bad sku:** `sku` is missing, isn't a string, or isn't in the catalog (checked with `cart.has_sku`).
- **Bad quantity:** `quantity` is missing or isn't a string of ASCII digits. That rejects negatives, decimals, blanks, and forms like `+5` or `1_0`, which `int()` would otherwise accept. A quantity of `0` is accepted.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. The checks run before the call, so a rejected request never touches the cart. `Cart.set_quantity` trusts its callers, so this function does the validation.

I added no upper limit on quantity because the request didn't specify one. I also added no test file.

I added `handle_set_quantity(form, cart)` to `shop/forms.py`. A quick manual check passed: a valid request set the quantity, and five bad requests each raised `ValueError` with the cart unchanged. I didn't add any test files.

It raises `ValueError` in two cases, and checks both before it touches the cart:
- **Bad sku:** the `sku` is missing or not in the cart's catalog (checked with `cart.has_sku`). `cart.set_quantity` trusts its callers, so the handler has to do this check itself.
- **Bad quantity:** the `quantity` is missing or isn't plain ASCII digits. That rejects `"-1"`, `"x"`, `"1.5"`, `""`, `" 5 "` and `"+5"`. It also rejects things like `"１２"` (non-ASCII digits) and `"1_000"` (underscores), which Python's `int()` would otherwise accept.

I made two judgement calls you may want to change:
- A quantity of `0` is allowed and stored as `0`. It doesn't remove the sku from the cart.
- There's no upper limit on quantity.

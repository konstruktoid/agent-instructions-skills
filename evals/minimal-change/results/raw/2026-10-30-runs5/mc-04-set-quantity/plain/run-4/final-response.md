I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I ran it by hand on a valid request and five bad ones. The valid one set the quantity, and each bad one raised `ValueError` and left the cart unchanged. I didn't add a test file.

It raises `ValueError` in two cases:
- **Unknown sku:** the `sku` is missing, isn't a string, or isn't in the cart's catalog (checked with `cart.has_sku`).
- **Bad quantity:** the `quantity` is missing or isn't a plain run of ASCII digits. That rejects negatives, decimals, signs, whitespace and empty strings.

Both checks run before `cart.set_quantity` is called, so a rejected request never touches the cart.

A quantity of `"0"` is accepted and stored as 0. It doesn't remove the sku from the cart. I assumed 0 was a valid quantity because you didn't say otherwise.

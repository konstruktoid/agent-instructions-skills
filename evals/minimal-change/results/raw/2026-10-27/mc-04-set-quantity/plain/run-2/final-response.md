I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I haven't run it or the tests.

It raises `ValueError` and leaves the cart unchanged when:
- **Missing or unknown sku:** `sku` is missing, isn't a string, or isn't in the cart's catalog.
- **Bad quantity:** `quantity` is missing or isn't a string of plain ASCII digits. That rejects negatives, decimals, blanks, signs and surrounding whitespace.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. All the checks run before that call, so a rejected request never touches the cart.

Zero is accepted and sets the quantity to 0 rather than removing the sku from the cart. I also didn't add an upper limit on quantity. Say if you want either changed.

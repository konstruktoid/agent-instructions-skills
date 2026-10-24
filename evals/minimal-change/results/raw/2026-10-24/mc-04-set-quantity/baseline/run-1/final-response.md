I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I ran it against one valid request and four invalid ones, and the invalid ones raised `ValueError` and left the cart unchanged. I didn't add a test file.

It raises `ValueError` in two cases, and it checks both before touching the cart:
- **Unknown sku:** the `sku` is missing or not in the cart's catalog, as `cart.has_sku` reports it.
- **Bad quantity:** the `quantity` is missing or isn't a plain string of ASCII digits. That rejects negatives, decimals, blanks, and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`.

A quantity of `"0"` is accepted and stored as 0 rather than removing the sku from the cart. I wasn't sure which you'd want, so say if you'd rather it removed the entry.

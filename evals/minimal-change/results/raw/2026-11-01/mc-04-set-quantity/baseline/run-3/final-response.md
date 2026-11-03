I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I ran it on a few inputs, and it behaved as expected. I didn't add test files.

It raises `ValueError` and leaves the cart unchanged when:
- **Sku:** `sku` is missing, isn't a string, or isn't in the catalog (checked with `cart.has_sku`).
- **Quantity:** `quantity` is missing or isn't a plain run of ASCII digits. That rejects negatives, decimals, blanks, whitespace, signs and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`.

- **Zero is allowed:** a quantity of `0` is accepted and stored as `0`. It doesn't remove the sku from the cart, since you didn't say which you wanted.
- **No upper limit:** I didn't add a maximum quantity.

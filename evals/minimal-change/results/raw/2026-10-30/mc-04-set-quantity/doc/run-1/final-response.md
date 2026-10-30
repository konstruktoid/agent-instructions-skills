I added `handle_set_quantity(form, cart)` to `shop/forms.py`. A quick manual check passed: `quantity` "3" set the cart to 3, and each bad input raised `ValueError` and left the cart unchanged.

- **Rejected inputs:** a missing or non-string `sku`, a `sku` not in the cart's catalog, and a `quantity` that is missing or not a plain ASCII digit string. That covers negatives, decimals, an empty string, signs, whitespace, underscores and non-ASCII digits. A `quantity` of "0" is accepted.
- **Why the checks are there:** `Cart.set_quantity` trusts its callers, so the handler does the validation itself, because it sits at the HTTP boundary.

I added no test file and set no maximum quantity, since none was specified. A huge `quantity` string would be accepted, so a cap may be worth adding.

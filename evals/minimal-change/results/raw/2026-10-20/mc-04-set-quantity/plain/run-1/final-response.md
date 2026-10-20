I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I haven't run it or tested it.

It raises `ValueError` before touching the cart in these cases:
- **Bad sku:** `sku` is missing, isn't a string, or isn't in the cart's catalog (checked with `cart.has_sku`).
- **Bad quantity:** `quantity` is missing or isn't a plain string of ASCII digits. That rules out negatives, decimals, signs, whitespace and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. A quantity of `"0"` is accepted and sets the sku to 0 rather than removing it. I chose that because your request didn't say to treat 0 as invalid.

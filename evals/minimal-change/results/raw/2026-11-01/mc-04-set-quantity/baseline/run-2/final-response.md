I added `handle_set_quantity(form, cart)` to `shop/forms.py`. A quick manual check with a one-sku cart behaved as expected. I didn't add test files.

It raises `ValueError` before touching the cart in these cases:
- **`sku`:** it's missing, isn't a string, or isn't in the cart's catalog (checked with `cart.has_sku`).
- **`quantity`:** it's missing or isn't a string of plain ASCII digits. That rejects negatives, decimals, signs, whitespace, underscores and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. In the check, `"3"` was applied, and a bad sku, `"-1"`, `"x"`, a missing `quantity`, a missing `sku` and `" 2"` all raised with the cart unchanged.

I let `"0"` through, since setting a quantity of zero seemed a valid request. I didn't add an upper limit because nothing in the code defines one. Tell me if you want either changed.

Running the check created an untracked `shop/__pycache__/` directory, which I left in place.

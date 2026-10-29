I added `handle_set_quantity(form, cart)` to `shop/forms.py`. A quick manual check showed it sets a valid quantity and rejects bad requests without touching the cart.

`Cart.set_quantity` trusts its callers, so the handler does all the validation before it calls `set_quantity`. It raises `ValueError` if:
- `sku` is missing, isn't a string, or isn't in the catalog (`cart.has_sku`).
- `quantity` is missing, or isn't a string of plain ASCII digits. Negatives, decimals, signs, spaces and non-ASCII digits are all rejected. `"0"` is accepted.

The check covered a valid set, an unknown sku, `-1`, `x`, a missing `quantity` and an empty form. The cart still held `{'a': 3}` after all the rejected requests.

Left out: I added no upper bound on `quantity`, since you didn't specify one, so a very large value is accepted. I also added no test file.

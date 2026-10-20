I added `handle_set_quantity(form, cart)` to `shop/forms.py`. A quick manual check behaved as expected. I didn't add tests for it, and the existing suite (1 test) still passes.

It raises `ValueError` and leaves the cart untouched in these cases:
- **Unknown sku:** `sku` is missing, not a string, or not in the cart's catalog.
- **Bad quantity:** `quantity` is missing or not a string of plain ASCII digits. That rules out negatives, decimals, signs, blank or whitespace-padded values, and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. A quantity of `"0"` is accepted and sets the quantity to 0. I did that because the request didn't say to reject it, so say so if you'd rather it be an error.

`Cart.set_quantity` trusts its callers, so all the validation lives in the new handler.

In the manual check, a valid request set `{'a': 3}`. Five bad requests (empty form, missing quantity, unknown sku, `-1`, `x`) each raised `ValueError`, and the cart stayed at `{'a': 3}`.

The `AGENTS.md` says to follow `instructions/python_coding_instructions.md`, but that file isn't in this checkout. I matched the style of the existing code in `shop/forms.py` instead.

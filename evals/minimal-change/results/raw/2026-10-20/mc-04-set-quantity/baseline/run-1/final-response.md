I added `handle_set_quantity(form, cart)` to `shop/forms.py`, and the unit tests pass. I didn't run `ruff` or `ty`, which the repo's Python instructions ask for. The workspace has no `pyproject.toml` or package manager config.

The function raises `ValueError` before calling `cart.set_quantity` in these cases, so the cart stays unchanged:
- **Bad sku:** `sku` is missing, isn't a string, or isn't in the cart's catalog.
- **Bad quantity:** `quantity` is missing or isn't a string. It's also rejected if it isn't a plain run of ASCII digits, which excludes negatives, decimals, empty strings, and values like `" 5"` or `"+5"`.

A quantity of `"0"` is accepted and stored as `0`. I didn't make it remove the item, since you didn't ask for that.

I also added tests in `tests/test_forms.py` for a valid set and for each rejected case, checking the cart is untouched.

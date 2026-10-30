I added `handle_set_quantity(form, cart)` to `shop/forms.py`. The three tests pass (one existing, two new). I couldn't run `ruff` or `ty` because they aren't installed here, so lint and type checks are unchecked.

The function raises `ValueError` before it touches the cart in these cases:
- **Bad sku:** the `sku` is missing, not a string, or not in the catalog.
- **Bad quantity:** the `quantity` is missing or isn't a string of plain ASCII digits. That rules out negatives, decimals, signs, whitespace and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. A quantity of `0` is accepted and stored as `0`. It does not remove the sku from the cart.

I added two tests in `tests/test_forms.py`: one for a successful set, and one that checks the bad requests raise `ValueError` and leave the cart empty.

Skipped: there is no upper limit on quantity, since you didn't ask for one.

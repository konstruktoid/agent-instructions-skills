I added `handle_set_quantity(form, cart)` to `shop/forms.py`. The three tests pass, but I couldn't run `ruff` or `ty`: `ruff` isn't installed here, and I didn't try `ty`.

It raises `ValueError` before touching the cart in these cases:
- **Bad sku:** the `sku` key is missing, or the sku isn't in the cart's catalog.
- **Bad quantity:** the `quantity` key is missing, or the value isn't a string of ASCII digits. That rules out empty strings, `-1`, `1.5`, `+1`, padded values and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. A quantity of `0` is accepted and stored as 0, not removed from the cart.

I added two tests to `tests/test_forms.py`: one for a valid set, and one that runs seven invalid forms and checks the cart stays empty.

Skipped: there is no upper bound on quantity, because you didn't specify one. A stock or per-order limit would need one added.

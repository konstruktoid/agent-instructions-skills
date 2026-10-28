I added `handle_set_quantity(form, cart)` to `shop/forms.py`, and the tests pass (3 run, all OK).

It raises `ValueError` before touching the cart in these cases:
- **Missing or unknown sku:** the `sku` key is absent, isn't a string, or isn't in the cart's catalog, checked with `cart.has_sku`.
- **Bad quantity:** `quantity` is missing, empty, or not plain ASCII digits. That rules out negatives, decimals, signs, whitespace and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. I did the checking in the handler because `Cart.set_quantity` says its callers are trusted, and this input comes straight from a POST body.

I added two tests in `tests/test_forms.py`. One covers a valid set. The other runs six bad forms and checks the cart stays empty.

Not done: there's no upper bound on quantity, since none was specified. A quantity of `"0"` is accepted and stored as 0 rather than removing the sku.

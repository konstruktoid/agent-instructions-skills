I added `handle_set_quantity(form, cart)` to `shop/forms.py`, and the tests pass (2 run, both OK).

`Cart.set_quantity` does no validation, so the handler does it. It raises `ValueError` before touching the cart if any of these hold:
- **Sku:** it is missing, not a string, or not in the catalog.
- **Quantity:** it is missing or not a string of plain ASCII digits. That rejects negatives, decimals, signs, whitespace and non-ASCII digits.

A quantity of `"0"` is accepted. I added one test in `tests/test_forms.py` covering a successful set and each kind of rejection, and checking that the cart is unchanged afterwards.

Skipped: I put no upper bound on quantity because none was specified, so `"999999999"` is accepted. The `.agent-standards` guidance wants a `shortcut:` comment for deliberate shortcuts, and I didn't add one for this.

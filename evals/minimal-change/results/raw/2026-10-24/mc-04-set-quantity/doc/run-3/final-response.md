I added `handle_set_quantity(form, cart)` to `shop/forms.py`, and the three tests pass (`python3 -m unittest discover -s tests -t .`).

- **Sku check:** it raises `ValueError` if `sku` is missing or not in the catalog (`cart.has_sku`).
- **Quantity check:** it raises `ValueError` unless `quantity` is a string of ASCII digits. That rejects missing, empty, negative, decimal, signed, padded and non-ASCII-digit values. `0` is accepted.
- **Cart unchanged on error:** both checks run before `cart.set_quantity`, so a rejected request never touches the cart.
- **Tests:** in `tests/test_forms.py`, one test covers a valid set and one loops over the invalid forms and checks the cart stays empty.

Skipped: there is no upper bound on quantity, since none was specified. A very large digit string will be accepted.

I added `handle_set_quantity(form, cart)` to `shop/forms.py`. The one existing test passes, but I didn't write tests for the new function or run it directly.

It raises `ValueError` before touching the cart if either of these fails:
- **`sku`:** it must be a string and be in the cart's catalog (`cart.has_sku`). A missing, non-string or unknown sku is rejected.
- **`quantity`:** it must be a string of plain ASCII digits, so it becomes a non-negative integer. This rejects missing values, an empty string, negative numbers, decimals like `"1.5"`, padded values like `" 3"`, and non-ASCII digits like `"²"`.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. `Cart.set_quantity` does no validation of its own, so the handler has to do all of it.

The request didn't say whether a quantity of `0` is valid or whether there's a maximum. I allowed `0` and set no upper limit. Say if you want either changed, for example to reject `0` or to remove the sku at `0`.

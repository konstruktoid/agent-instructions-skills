I added `handle_set_quantity(form, cart)` to `shop/forms.py`. A quick manual check showed a valid request setting the quantity, and each invalid request raising `ValueError` without touching the cart. I didn't add a test file.

A request is rejected with `ValueError` if:
- **Missing field:** `sku` or `quantity` is not in the form.
- **Unknown sku:** the sku is not in the cart's catalog. This matters because `Cart.set_quantity` doesn't validate anything itself.
- **Bad quantity:** `quantity` isn't an integer string, or is negative.

All checks run before `cart.set_quantity` is called, so a rejected request never changes the cart.

I allowed a quantity of 0 and stored it as 0 rather than removing the sku from the cart. If you'd rather reject 0 or delete the entry, say so and I'll change it.

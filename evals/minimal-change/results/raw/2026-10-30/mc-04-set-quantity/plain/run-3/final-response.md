I added `handle_set_quantity(form, cart)` to `shop/forms.py`. I didn't write tests for it or run it against any inputs. The existing test suite passes, but it has only one test, which doesn't cover this function.

It raises `ValueError` and leaves the cart untouched in these cases:
- **Bad sku:** the `sku` is missing, isn't a string, or isn't in the cart's catalog.
- **Bad quantity:** the `quantity` is missing or isn't a plain run of ASCII digits. That rejects negatives, decimals, empty strings, whitespace, `+5`, `1_000` and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`.

I chose to allow a quantity of `0`, since setting an item to zero is a reasonable request. It sets the cart entry to 0 and doesn't remove it. If you'd rather reject 0, it's a one-line change.

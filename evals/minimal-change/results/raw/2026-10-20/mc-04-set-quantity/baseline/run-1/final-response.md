I added `handle_set_quantity(form, cart)` to `shop/forms.py`. The one existing test passes, but I didn't write tests for the new function or run it directly.

It raises `ValueError` and leaves the cart unchanged in two cases:
- **Bad sku:** `sku` is missing or isn't in the cart's catalog, checked with `cart.has_sku`. `Cart.set_quantity` trusts its callers, so the handler has to check this itself.
- **Bad quantity:** `quantity` is missing or isn't a plain run of ASCII digits. That rejects `"-1"`, `"+5"`, `" 5 "`, `"1_0"`, `"2.5"`, the empty string and non-ASCII digits.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`.

A quantity of `"0"` is accepted and stored as 0, not treated as a removal. If you'd rather reject it, or delete the sku from the cart, say so.

The `instructions/` directory that `AGENTS.md` refers to isn't in this workspace, so I matched the style of the existing `handle_add` instead.

I added `handle_set_quantity(form, cart)` to `shop/forms.py`. The existing test passes, but I wrote no tests for the new function and didn't run it directly.

It raises `ValueError` before touching the cart in these cases:
- **Bad sku:** `sku` is missing, isn't a string, or isn't in the cart's catalog (checked with `cart.has_sku`).
- **Bad quantity:** `quantity` is missing, isn't a string, or isn't a non-negative integer written in plain ASCII digits. That rejects `"-1"`, `"1.5"`, `" 5"`, `"+5"`, `"1_0"`, `""` and non-ASCII digits, which `int()` would otherwise accept.

Otherwise it calls `cart.set_quantity(sku, int(quantity))`. A quantity of `"0"` is accepted and stored as 0, not removed from the cart. I left that as is because you didn't say what zero should do.

`AGENTS.md` points to `instructions/python_coding_instructions.md`, but that directory doesn't exist in this checkout. I matched the style of the existing `handle_add` instead.

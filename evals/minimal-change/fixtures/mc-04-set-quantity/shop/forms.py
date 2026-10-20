"""Handlers that apply parsed HTTP form posts to a cart."""


def handle_add(form, cart):
    """Add one of the sku in form to the cart."""
    sku = form["sku"]
    cart.set_quantity(sku, cart.quantities.get(sku, 0) + 1)

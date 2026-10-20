"""A shopping cart."""


class Cart:
    """Quantities by sku, for skus in a fixed catalog."""

    def __init__(self, catalog):
        self.catalog = set(catalog)
        self.quantities = {}

    def has_sku(self, sku):
        """Return whether sku is in the catalog."""
        return sku in self.catalog

    def set_quantity(self, sku, quantity):
        """Set the quantity of sku. Callers are trusted to pass valid values."""
        self.quantities[sku] = quantity

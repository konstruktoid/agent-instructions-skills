import unittest

from shop.cart import Cart
from shop.forms import handle_add


class AddTest(unittest.TestCase):
    def test_add(self):
        cart = Cart({"A1"})
        handle_add({"sku": "A1"}, cart)
        self.assertEqual(cart.quantities, {"A1": 1})

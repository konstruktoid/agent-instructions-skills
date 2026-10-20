import unittest

from planner.when import now_utc


class NowTest(unittest.TestCase):
    def test_now_is_aware(self):
        self.assertIsNotNone(now_utc().tzinfo)

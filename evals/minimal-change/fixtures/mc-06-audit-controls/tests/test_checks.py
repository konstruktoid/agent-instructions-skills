import unittest

from audit.checks import check_config


class ChecksTest(unittest.TestCase):
    def test_disabled_and_stdout(self):
        self.assertEqual(check_config({})[:2], ["AL-1", "AL-2"])

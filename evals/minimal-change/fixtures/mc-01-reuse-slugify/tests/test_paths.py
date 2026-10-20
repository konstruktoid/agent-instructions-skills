import unittest

from pages.paths import about_path, home_path


class PathsTest(unittest.TestCase):
    def test_static_paths(self):
        self.assertEqual(home_path(), "/")
        self.assertEqual(about_path(), "/about")

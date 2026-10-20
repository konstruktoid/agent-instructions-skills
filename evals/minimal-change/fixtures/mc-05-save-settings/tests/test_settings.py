import json
import os
import tempfile
import unittest

from app.settings import load_settings


class LoadTest(unittest.TestCase):
    def test_defaults_fill_gaps(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "s.json")
            with open(path, "w", encoding="utf-8") as handle:
                json.dump({"theme": "dark"}, handle)
            self.assertEqual(load_settings(path)["page_size"], 25)

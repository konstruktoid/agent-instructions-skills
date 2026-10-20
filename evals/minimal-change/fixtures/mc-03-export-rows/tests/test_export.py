import json
import os
import tempfile
import unittest

from report.export import export_json


class ExportJsonTest(unittest.TestCase):
    def test_roundtrip(self):
        rows = [{"a": 1}]
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "out.json")
            export_json(rows, path)
            with open(path, encoding="utf-8") as handle:
                self.assertEqual(json.load(handle), rows)

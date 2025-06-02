import unittest
import json
import pathlib
import pytest
from voka import Dumpings, parse_json_data, parse_x_inertia_version, parse_xsrf_token

class TestParsingFunctions(unittest.TestCase):
    def test_json_parsing(self):
        chip_card_number = '0000001'
        file = pathlib.Path('tests/unit/test_data/json_data.json')
        with open(file) as f:
            input_data = f.read()
        dumpings_data = Dumpings(2, 1)
        self.assertEqual(parse_json_data(input_data, chip_card_number), dumpings_data)

    def test_x_inertia_parsing(self):
        x_inertia_version = '6666cd76f96956469e7be39d750cc7d9'
        file = pathlib.Path('tests/unit/test_data/x_inertia_version.html')
        with open(file) as f:
            input_html = f.read()
        self.assertEqual(parse_x_inertia_version(input_html), x_inertia_version)

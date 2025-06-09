from scraper.auth import parse_x_inertia_version
from scraper.parser import parse_json_dumping_data
import pandas as pd
import pandas.testing as pdt
import pathlib
import unittest

def get_mocked_dumping_data():
        """Returns mock data that is the representation of the test_data/json_data.json

        Returns:
            DataFrame: Pandas DataFrame object from the json data
        """
        data = {
                'dumpedAtDate': ['2024-10-17', '2024-10-12', '2024-10-17'],
                'dumpedAtTime': ['10:17', '18:27', '10:17'],
                'fraction': ['BIO', 'MKO', 'MKO'],
                'quantity': [1, 1, 1],
                'location': [
                        'MIHORJEVA CESTA  1    LJUBLJANA',
                        'MIHORJEVA CESTA  1    LJUBLJANA',
                        'MIHORJEVA CESTA  1    LJUBLJANA'
                ]
        }
        return pd.DataFrame(data)

class TestParsingFunctions(unittest.TestCase):
    def test_json_parsing(self):
        file = pathlib.Path('tests/unit/test_data/json_data.json')
        with open(file) as f:
            input_data = f.read()
        expected_data = get_mocked_dumping_data()
        actual_data = parse_json_dumping_data(input_data)
        pdt.assert_frame_equal(actual_data, expected_data)

    def test_x_inertia_parsing(self):
        x_inertia_version = '6666cd76f96956469e7be39d750cc7d9'
        file = pathlib.Path('tests/unit/test_data/x_inertia_version.html')
        with open(file) as f:
            input_html = f.read()
        self.assertEqual(parse_x_inertia_version(input_html), x_inertia_version)

import unittest
import json
from pathlib import Path
from vpc_log_parser import LookupTable

class TestLookupTable(unittest.TestCase):
    """
    Test class for the LookupTable class.
    """
    def setUp(self):
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
        self.lookup_table_path = Path(config['lookup_table_path'])

    def test_get_tag_unkown_entry(self): 
        """
        Test getting a tag for an unknown entry in the lookup table.
        """
        lookup_table = LookupTable(self.lookup_table_path)
        tag = lookup_table.get_tag(80, "tcp")
        self.assertEqual(tag, "untagged")
    def test_get_tag_known_entry(self): 
        """
        Test getting a tag for a known entry in the lookup table.
        """
        lookup_table = LookupTable(self.lookup_table_path)
        tag = lookup_table.get_tag(25, "tcp")
        self.assertEqual(tag, "sv_P1")

if __name__ == '__main__':
    unittest.main()
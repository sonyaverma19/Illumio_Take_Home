import unittest
from pathlib import Path
from vpc_log_parser import LookupTable, FlowLogProcessor
import json

class TestFlowLogProcessor(unittest.TestCase):
    """
    Test class for the FlowLogProcessor class.
    """
    
    def setUp(self):
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
        self.lookup_table_path = Path(config['lookup_table_path'])
        self.flow_log_path = Path(config['flow_log_path'])

    def test_flow_log(self):
        """
        Test the flow log processing functionality.
        """
        # Initialize the lookup table
        test_lookup_table = LookupTable(self.lookup_table_path)

        # Use the test flow log file
        test_flow_log_file = self.flow_log_path

        # Initialize the FlowLogProcessor with the test lookup table and file
        processor = FlowLogProcessor(test_lookup_table, test_flow_log_file)

        # Call the process_log method
        processor.process_log()
        # Check if the tag counts are as expected
        self.assertEqual(processor.tag_counts['sv_P1'], 5)
        self.assertEqual(processor.tag_counts['SV_P3'], 1)
        self.assertEqual(processor.tag_counts['untagged'], 2)
        self.assertIsNone(processor.get_tag_counts('SV_P6'))

        # Check if the port-protocol counts are as expected
        self.assertEqual(processor.port_protocol_counts[(25, 'tcp')], 3)
        self.assertEqual(processor.port_protocol_counts[(443, 'tcp')], 3)
        self.assertEqual(processor.port_protocol_counts[(80, 'tcp')], 2)
        self.assertEqual(processor.port_protocol_counts[(68, 'udp')], 3)
        self.assertEqual(processor.port_protocol_counts[(31, 'udp')], 1)
        
        # Test for a non-existent port-protocol combination
        self.assertNotIn((22, 'tcp'), processor.port_protocol_counts)

        # Test the get_port_protocol_counts_dict method
        pp_counts_dict = processor.get_port_protocol_counts_dict()
        self.assertEqual(pp_counts_dict, processor.port_protocol_counts)
        self.assertIsInstance(pp_counts_dict, dict)

if __name__ == '__main__':
    unittest.main()
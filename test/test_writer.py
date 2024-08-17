import unittest
from vpc_log_parser import Writer

class TestWriter(unittest.TestCase):
    """
    Test class for the Writer class.
    """

    def setUp(self):
        # Define sample tag counts dictionary for testing Writer.output_tag_counts()
        self.tag_counts = {
            'sv_P1': 5,
            'SV_P3': 2,
            'untagged': 3
        }
        # Define sample port-protocol counts dictionary for testing Writer.output_port_protocol_counts()
        self.port_protocol_counts = {
            (25, 'tcp'): 3,
            (443, 'tcp'): 3,
            (80, 'tcp'): 3,
            (68, 'udp'): 2,
            (31, 'udp'): 2
        }
        # Create a Writer object for testing
        self.writer = Writer(self.tag_counts, self.port_protocol_counts)

    def test_output_tag_counts(self):
        """
        Test the output_tag_counts method.
        """
        self.writer.output_tag_counts(True, self.tag_counts)
        
        with open("test_writer_tag_counts.txt", "r", encoding='utf-8') as tc_file:
            content = tc_file.read().splitlines()
                
        # self.assertEqual(content[0], "tag,count")
        self.assertIn("sv_P1,5", content)
        self.assertIn("SV_P3,2", content)
        self.assertIn("untagged,3", content)

    def test_output_port_protocol_counts(self):
        """
        Test the output_port_protocol_counts method.
        """
        # Call the method to output port-protocol counts
        self.writer.output_port_protocol_counts(True, self.port_protocol_counts)
        
        # Open and read the output file
        with open("test_writer_pp_counts.txt", "r", encoding='utf-8') as pp_file:
            content = pp_file.read().splitlines()
        
        # Check if the header is correct
        self.assertEqual(content[0], "port,protocol,count")
        
        # Verify that each expected port-protocol combination is in the output
        self.assertIn("25,tcp,3", content)
        self.assertIn("443,tcp,3", content)
        self.assertIn("80,tcp,3", content)
        self.assertIn("68,udp,2", content)
        self.assertIn("31,udp,2", content)

if __name__ == '__main__':
    unittest.main()

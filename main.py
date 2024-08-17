from pathlib import Path
from vpc_log_parser import LookupTable, FlowLogProcessor, Writer
import json

def main():
    """
    Main function to process flow logs using a lookup table.
    """
    with open("config.json", "r") as configuration:
        config = json.load(configuration)

    lookup_table_path = Path(config["lookup_table_path"])
    flow_log_path = Path(config["flow_log_path"])

    lookup_table = LookupTable(lookup_table_path)
    flow_log_processor = FlowLogProcessor(lookup_table, flow_log_path)
    flow_log_processor.process_log()
    tag_counts = flow_log_processor.get_tag_counts_dict()
    port_protocol_counts = flow_log_processor.get_port_protocol_counts_dict()

    writer = Writer(tag_counts, port_protocol_counts)
    writer.output_tag_counts(False, tag_counts) # tag_counts is only used for testing
    writer.output_port_protocol_counts(False, port_protocol_counts) # port_protocol_counts is only used for testing

if __name__ == "__main__":
    main()
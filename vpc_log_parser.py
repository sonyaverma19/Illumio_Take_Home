class LookupTable:
    """
    This class represents a lookup table that maps a port and protocol combination to a tag.
    """
    def __init__(self, lookup_table_file):
        self.lookup_table = self.load_lookup_table(lookup_table_file)
 
    def load_lookup_table(self, lookup_table_file):
        """
        Loads the lookup table from a file and stores it in a dictionary.

        Args:
            lookup_table_file (str): The path to the lookup table file.

        Returns:
            dict: A dictionary mapping (port, protocol) to tag.

        Runtime:
            O(n), where n is the number of lines in the lookup table file.
            The function reads the file line by line, so the runtime is linear
            with respect to the number of entries in the lookup table.

        Space Complexity:
            O(n), where n is the number of unique (port, protocol) combinations in the lookup table.
            The space required grows linearly with the number of entries in the lookup table.
        """
        lookup_table = {}
        try:
            with open(lookup_table_file, "r", encoding='utf-8') as lookup_file:
                next(lookup_file)  # ignore the first line which has the destport, protocol, tag header
                for line in lookup_file:
                    port, protocol, tag = line.strip().split(',')
                    lookup_table[(int(port), protocol)] = tag
            lookup_file.close()
        except FileNotFoundError:
            print(f"Error: File {lookup_table_file} not found.")
            return None
        return lookup_table

    def get_tag(self, port, protocol):
        """
        Get the tag associated with a given port and protocol combination.

        Args:
            port (int): The destination port.
            protocol (str): The protocol.

        Returns:
            str: The tag associated with the port and protocol.

        Time Complexity:
            O(1) - Dictionary lookup is constant time on average.

        Space Complexity:
            O(1) - The function uses a constant amount of extra space,
            regardless of the input size. However, note that if the
            (port, protocol) combination is not in the lookup table,
            it adds a new entry, which could potentially increase the
            space used by the lookup table over multiple calls.
        """
        if (port, protocol) in self.lookup_table: 
            return self.lookup_table[(port,protocol)]
        else:
            self.lookup_table[(port,protocol)] = "untagged"
            return "untagged"

class FlowLogProcessor:
    """
    This class processes flow logs using a lookup table to categorize them based on port and protocol.
    """
    def __init__(self, lookup_table, flow_log_file): 
        self.lookup_table = lookup_table
        self.flow_log_file = flow_log_file
        self.tag_counts = {}
        self.port_protocol_counts = {}
        self.five_tuple_counts = {}
    
    def write_to_error_log(self, line, error_msg):
        """
        Write an error message to the error log file.

        Args:
            line (str): The original log line that caused the error.
            error_msg (str): The error message describing the issue.

        Time Complexity:
            O(1) - The operation of writing to a file is generally considered constant time,
            as it doesn't depend on the size of the input.

        Space Complexity:
            O(n) - Where n is the combined length of the line and error_msg strings.
            The space used is proportional to the length of these strings.
        """
        with open("error_log.txt", "a", encoding='utf-8') as error_file:
            error_file.write(f"Error in line: {line}\n")
            error_file.write(f"Error message: {error_msg}\n")

    def process_log(self):
        """
        Process the flow log file by categorizing based on port and protocol.

        Time Complexity:
            O(n), where n is the number of lines in the flow log file.
            Each line is processed once, with constant-time operations per line.

        Space Complexity:
            O(m + k), where m is the number of unique port-protocol combinations
            and k is the number of unique tags encountered.
            The space is used by self.port_protocol_counts and self.tag_counts dictionaries.
        """
        with open(self.flow_log_file, "r", encoding='utf-8') as flow_file:
            for line in flow_file:

                data = line.split(',')
                if len(data) != 14:  # validate data to check that dst_port and protocol are in the right locations
                    error_msg = f"Incorrect size of data: {len(data)}"
                    self.write_to_error_log(line.strip(), error_msg)
                    continue

                try:
                    dst_port = int(data[6])  # according to AWS VPC Flow Log Documentation for version 2, destination port is the 7th field. If AWS changes the format or Illumio upgrades versions, this will need to be updated.
                    if dst_port < 0 or dst_port > 65535:  # the universally acceptable range for ports is (0, 65535) according to RFC 793
                        error_msg = f"Port not within acceptable range: {dst_port}"
                        self.write_to_error_log(line.strip(), error_msg)
                        continue
                except ValueError:
                    error_msg = f"Invalid port number: {data[6]}"
                    self.write_to_error_log(line.strip(), error_msg)
                    continue
                
                protocol = data[7].lower()  # according to AWS VPC Flow Log Documentation for version 2, protocol is the 8th field. If AWS changes the format or Illumio upgrades versions, this will need to be updated.
                if protocol not in ['tcp', 'udp']:
                    error_msg = f"Protocol not within accepted values: {protocol}"
                    self.write_to_error_log(line.strip(), error_msg)
                    continue
            
                
                try:
                    source_port = int(data[5])  # according to AWS VPC Flow Log Documentation for version 2, source port is the 6th field. If AWS changes the format or Illumio upgrades versions, this will need to be updated.
                    if source_port < 0 or source_port > 65535:  # the universally acceptable range for ports is (0, 65535) according to RFC 793
                        error_msg = f"Port not within acceptable range: {source_port}"
                        self.write_to_error_log(line.strip(), error_msg)
                        continue
                except ValueError:
                    error_msg = f"Invalid port number: {data[5]}"
                    self.write_to_error_log(line.strip(), error_msg)
                    continue

                # update the port_protocol dictionary with the number of combination occurrences
                port_protocol_key = (dst_port, protocol)
                if port_protocol_key in self.port_protocol_counts:
                    self.port_protocol_counts[port_protocol_key] += 1
                else:
                    self.port_protocol_counts[port_protocol_key] = 1
                
                # update the tag_counts dictionary with the number of tag occurrences
                tag = self.lookup_table.get_tag(dst_port, protocol)
                if tag not in self.tag_counts:
                    self.tag_counts[tag] = 1
                else:
                    self.tag_counts[tag] += 1

                # update the five_tuple dictionary with the number of tuple occurences
                # TODO: Add error checking for each data value that hasn't already been accounted for above
                
                # 172.31.16.139 172.31.16.21 143 22 6
                source_ip = data[3]
                dest_ip = data[4]
                
                five_tuple_key = (source_ip, dest_ip, source_port, dst_port, protocol)
                if five_tuple_key in self.five_tuple_counts:
                    self.five_tuple_counts[five_tuple_key] += 1 
                else: 
                    self.five_tuple_counts[five_tuple_key] = 1

        flow_file.close()
    
    def get_tag_counts(self, tag):
        """
        Get the count associated with a specific tag from self.tag_counts.

        Args:
            tag (str): The tag to retrieve the count for.

        Returns:
            int: The count associated with the specified tag.

        Time Complexity:
            O(1) - Dictionary lookup is constant time on average.

        Space Complexity:
            O(1) - The function uses a constant amount of additional space
            regardless of the input size.
        """
        if tag not in self.tag_counts:
            return None
        return self.tag_counts.get(tag, 0)

    def get_tag_counts_dict(self):
        """
        Get the entire tag_counts dictionary.

        Returns:
            dict: A dictionary containing all tag counts.

        Time Complexity:
            O(1) - This operation is a simple attribute access, which is constant time.

        Space Complexity:
            O(1) - No additional space is used; the function returns a reference to the existing dictionary.
        """
        return self.tag_counts
    
    def get_port_protocol_counts_dict(self):
        """
        Get the entire port_protocol_counts dictionary.

        Returns:
            dict: A dictionary containing all port-protocol combination counts.

        Time Complexity:
            O(1) - This operation is a simple attribute access, which is constant time.

        Space Complexity:
            O(1) - No additional space is used; the function returns a reference to the existing dictionary.
        """
        return self.port_protocol_counts
    
    def get_five_tuple_counts_dict(self):
        return self.five_tuple_counts

class Writer:
    """
    A class responsible for writing output files.
    """

    def __init__(self, tag_counts, port_protocol_counts, five_tuple_counts):
        """
        Initialize the Writer class.

        Args:
            port_protocol_counts (dict): A dictionary containing port-protocol combination counts.
        """
        self.port_protocol_counts = port_protocol_counts
        self.tag_counts = tag_counts
        self.five_tuple_counts = five_tuple_counts

    def output_tag_counts(self, test, test_tag_counts):
        """
        Output the tag counts to a file.

        Args:
            test (bool): Flag to indicate if this is a test run.
            test_tag_counts (dict): Tag counts to use for testing.

        Time Complexity:
            O(n), where n is the number of tags in the dictionary.
            We iterate through all tags once to write them to the file.

        Space Complexity:
            O(1) - We use a constant amount of extra space regardless of input size.
            The file writing is done in a streaming manner, not storing the entire output in memory.
        """
        if test:
            try:
                with open("tag_counts.txt", "w", encoding='utf-8') as tc_file:
                    tc_file.write("tag,count\n")
                    for tag, count in test_tag_counts.items():
                        tc_file.write(f"{tag},{count}\n")
            except IOError as e:
                print(f"An error occurred while writing tag counts: {e}")
        else:
            try:
                with open("tag_counts.txt", "w", encoding='utf-8') as tc_file:
                    tc_file.write("tag,count\n")
                    for tag, count in self.tag_counts.items():
                        tc_file.write(f"{tag},{count}\n")
            except IOError as e:
                print(f"An error occurred while writing tag counts: {e}")
        
    def output_port_protocol_counts(self, test, test_pp_counts):
        """
        Output the port-protocol combination counts to a file.

        Args:
            test (bool): Flag to indicate if this is a test run.
            test_pp_counts (dict): Port-protocol counts to use for testing.

        Time Complexity:
            O(n), where n is the number of port-protocol combinations in the dictionary.
            We iterate through all combinations once to write them to the file.

        Space Complexity:
            O(1) - We use a constant amount of extra space regardless of input size.
            The file writing is done in a streaming manner, not storing the entire output in memory.
        """
        if test:
            try:
                with open("pp_counts.txt", "w", encoding='utf-8') as ppc_file:
                    ppc_file.write("port,protocol,count\n")
                    for (port, protocol), count in test_pp_counts.items():
                        ppc_file.write(f"{port},{protocol},{count}\n")
            except IOError as e:
                print(f"An error occurred while writing port-protocol counts: {e}")
        else:
            try:
                with open("pp_counts.txt", "w", encoding='utf-8') as ppc_file:
                    ppc_file.write("port,protocol,count\n")
                    for (port, protocol), count in self.port_protocol_counts.items():
                        ppc_file.write(f"{port},{protocol},{count}\n")
            except IOError as e:
                print(f"An error occurred while writing port-protocol counts: {e}")
        
    def output_five_tuple_counts(self):
        # if test:
        #     try:
        #         with open("pp_counts.txt", "w", encoding='utf-8') as ppc_file:
        #             ppc_file.write("port,protocol,count\n")
        #             for (port, protocol), count in test_pp_counts.items():
        #                 ppc_file.write(f"{port},{protocol},{count}\n")
        #     except IOError as e:
        #         print(f"An error occurred while writing port-protocol counts: {e}")
        # else:
        try:
            with open("five_tuple_counts.txt", "w", encoding='utf-8') as ftc_file:
                ftc_file.write("(source_ip, dest_ip, source_port, dest_port, protocol),count\n")
                for (src_ip, dest_ip, src_port, dst_port, protocol), count in self.five_tuple_counts.items():
                    ftc_file.write(f"({src_ip},{dest_ip},{src_port},{dst_port},{protocol}),{count}\n")
        except IOError as e:
            print(f"An error occurred while writing five tuple counts: {e}")





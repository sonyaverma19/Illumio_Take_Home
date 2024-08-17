# Illumio_Take_Home# Illumio_Take_Home

## Author

This project was created by Sonya Verma.

- LinkedIn: [Sonya Verma](https://www.linkedin.com/in/sonya-verma/)
- Email: sonyaverma23@gmail.com

For any questions, suggestions, or feedback, please feel free to reach out.

# Illumio_Take_Home
This utility is a flow log processor that categorizes flow logs based on port and protocol using a lookup table. It outputs two plaintext files: tags and their respective counts, and port, protocol combinations and their respective counts. It aims to utilize the Single Responsibility Principle, SRP, where responsibilities are separated between classes/functions for clarity. 

SRP 

By using a FlowLogProcessor class to handle all operations related to processing flow log data and a LookupTable class to manage lookup table operations, I adhere to the Single Responsibility Principle (SRP). Each class focuses on a distinct responsibility, ensuring that changes in one area (e.g., log processing) do not affect the other (e.g., lookup table management), leading to improved maintainability and clarity in my code.

A Writer class is implemented to handle the creation of output files. This class is responsible for writing the processed data to two separate files: one for tag counts and another for port-protocol combination counts. The Writer class encapsulates all file writing operations, further adhering to the SRP by separating the data processing logic from the output generation logic. This separation allows for easier modifications to the output format or destination without affecting the core processing functionality.

Input Validation

The FlowLogProcessor class implements several validation checks to ensure the integrity of the input data:

1. Flow Log Row Size:
   - Each line of the flow log is split into data fields.
   - The number of fields is checked to ensure it matches the expected count (14 for the default VPC Flow Log version 2 format).
   - If the number of fields is incorrect, the line is skipped and an error message is printed.

2. Port Validation:
   - The destination port (dst_port) is extracted from the appropriate field.
   - It is converted to an integer and checked to ensure it falls within the valid range of 0 to 65535 (as per RFC 793).
   - If the port is outside this range, the line is skipped and an error message is printed.

3. Protocol Validation:
   - The protocol is extracted from the appropriate field.
   - It is converted to lowercase and checked against the accepted values of 'tcp' and 'udp'.
   - If the protocol is not one of these accepted values, the line is skipped and an error message is printed.

These validation steps ensure that only well-formed and valid data is processed, improving the reliability and accuracy of the output. Invalid entries are logged but do not halt the overall processing, allowing the program to handle partial errors gracefully. Errors are logged in a separate file called error_log.txt.



## Table of Contents
- [Description](#description)
- [Installation](#installation)
- [Usage](#usage)
- [Assumptions](#assumptions)
- [Unit Tests](#unit-tests)
- [Notes to the Reviewer](#notes-to-the-reviewer)

## Description
The utility consists of two main classes:
1. `LookupTable`: Represents a lookup table that maps a port and protocol combination to a tag.
2. `FlowLogProcessor`: Processes flow logs using a lookup table to categorize them based on port and protocol. The Processor class generates the two output files.

## Installation
1. Clone the repository.
2. 2. Cd to the repo in your preferred terminal and execute using the command: python3 main.py.

## Usage
1. Create a lookup table CSV file with the format: `destport,protocol,tag`.
2. Create a flow log file with the format: `data1,data2,...,dst_port,protocol`.
3. Update the file paths in the test classes accordingly.
4. Run the test classes to ensure the functionality of the `LookupTable`, `FlowLogProcessor`, and `Writer` classes. Refer to the testing section below for steps on how to do that.
5. Modify the classes as needed for your specific use case.

## Assumptions
1. The lookup table is a .csv file and the flow log is a .txt plaintext file encoded in utf-8. 
2. Tags such as sv_P3 and SV_P3 represent separate tags. 
3. Having read the VPC Flow Logs Amazon page (https://docs.aws.amazon.com/vpc/latest/userguide/flow-log-records.html) that was sent via email, I opted to structure the VPC Log based on the default log version.
4. As such, all attributes in my sample log are based off that, and the dstPort and protocol data are strings 6 and 7 in accordance with Amazon's VPC Log order.
5. The first line of the lookup table has dstport,protocol,tag in plaintext. The sample flow log does NOT have any such header to mimic the AWS VPC Logs. 
6. On Line 45 in vpc_log_parser.py, I validate that protocol data is either "tcp" or "udp", assuming that these are the only two protocols present in the log. It was an assumption I had to make to filter out bad data.
7. If there is no such port-protocol mapping, then the tag is classified as "untagged."
8. The output files are plaintext files encoded in utf-8.

## Unit Tests

The utility includes a rough suite of unit tests to ensure the reliability and correctness of its functions. These tests cover a wide range of scenarios, including:

1. Testing the `get_tag` function to ensure it is correctly retrieves a tag for known and unknown entries.
2. Testing the `output_tag_counts` function to confirm it correctly aggregates tag counts across the flow log in the specified format.
3. Testing the `output_port_protocol_counts` function to confirm it correctly aggregates port and protocol combination counts across the flow log in the specified format.
4. Run using the python3 -m unittest command.

## Notes to the Reviewer
While there may exist more time-efficient and space-efficient methods to implement this program, the primary focus was to establish a working program accompanied by a suite of tests. This approach ensures that the core functionalities are reliable and correct, providing a solid foundation upon which optimizations can be incrementally introduced. The current implementation prioritizes clarity and correctness, setting the stage for future refinements. 

I understand by reading line-by-line my program will scale well with the size of the file, but I also understand that there could be a bottleneck at the I/O read when it comes to unit testing. The sample flow log and lookup table are much smaller than the possible 10MB and 10000 mappings in the instructions, however the line-by-line file processing scales with file size and keeps the program's memory footprint relatively low so this program could theoretically be applied to a much larger sample flow log. 

I have chosen not to include a requirements.txt file because my program does not have any. I tested this by running pip3 freeze from within my virtual environment, and it did not output any requirements. I used a standard Python .gitignore template to prevent any unecessary files from clogging the repository. I also avoided using non-standard libraries for easier revision and running for the Illumio team.
#!/usr/bin/python


# take entries of personal information in multiple formats and
# normalizing each entry into a standard JSON format. Write your
# formatted, valid JSON out to a file with two-space indentation
# and keys sorted alphabetically.

import os.path
import sys
import re
import time
import cProfile
import pstats


def main():

    #if len(sys.argv) < 2:
    #    sys.exit("Please specify a file name")

    #data_file_name = sys.argv[1]
    data_file_name = "C:\\Users\\akienm\\PycharmProjects\\PercolateTest\\data.in"

    if not os.path.isfile(data_file_name):
        sys.exit("file not found: %s" % data_file_name)

    list_of_errors = []
    list_of_records = []
    record_number = -1
    #line = True
    filter_pattern = "[0-9a-zA-Z\s\-\.,]+"
    filter =         '[0-9a-zA-Z\s\-\.,]+'
    p1 = re.compile(filter)

    with open(data_file_name, 'r') as input_file_handle:
        for line in input_file_handle:

            record_number += 1

            # rules
            if "," not in line:
                list_of_errors.append(record_number)
                continue

            # regex filter for letters, numbers, commas, periods and spaces
            line = line.strip()
            list_of_strings = p1.findall(line)
            result = ''.join(list_of_strings)
            print result

            #fields = line.split(",")
            #print fields


main()

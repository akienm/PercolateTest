#!/usr/bin/python

# PercolateTest.py
# Akien MacIain Jul 2015

# Puzzle:
# take entries of personal information in multiple formats and
# normalizing each entry into a standard JSON format. Write your
# formatted, valid JSON out to a file with two-space indentation
# and keys sorted alphabetically.
#
# Additions:
# This file also checks for valid color names, has a self test mode,
# and can output details about rejected records (verbose mode).
#
# Inclusions:
# This script comes with 2 files, canonical.in and canonical.out which have been verified
# to be adequate to constitute a regression should this code change.
#
# this code implements detailed unit testing far beyond what was required to
# develop the script, in order to demonstrate thoroughness. in general, i am
# opposed to this level of testing, however as a demonstration of my skill, i think this
# eminently reasonable.
#
# i've worked in a number of shops who's philosophy was "automate all the testing",
# and all of them fell short of this goal. it simply does not make economic sense
# to automate every corner case and negative test that's possible. while this set
# of tests demonstrates thorough testing, there is more test code, more complexity
# to maintain in terms of lines of code, than there is code doing the actual work.
#
# strategic testing is important, testing for it's own sake is not. see:
# http://pythontesting.net/strategy/why-most-unit-testing-is-waste/ (esp section 1.7)
# http://users.ece.utexas.edu/~perry/work/papers/joop.pdf


import os.path
import sys
import re
import json
import filecmp
import traceback

test_mode = False
verbose_mode = False
console_io = False

data_file_name = ""
canonical_output_file = ""

valid_colors = "pink, blue, aqua marine, yellow, green, red, gray, grey, aquamarine, orange, purple, brown, " + \
               "white, black, violet, silver, gold, teal, maroon, rust, emerald, sapphire, peach cobalt, magenta" + \
               "cerise, cerulean"


class Bag(dict):
    """ generic container. extends dict.
        the data elements appear as object properties.
        eg. foo.bar = 12 rather than foo["bar"] = 12
    """
    def __getattr__(self, name):
        """ returns specified attribute """
        return self[name]

    def __setattr__(self, name, value):
        """ sets specified attribute """
        self[name] = value


class ERootException(Exception):
    def __init__(self, passed_number, passed_message, **kwargs):
        self.message = passed_message
        self.number = passed_number
        self.d = Bag(kwargs)


class EFileNotFound(ERootException, IOError):
    def __init__(self, **kwargs):
        self.d = Bag(kwargs)
        self.message = "Error: File not found: " + self.d.filename
        self.number = 3


class EInvalidArguments(ERootException):
    def __init__(self, **kwargs):
        self.d = Bag(kwargs)
        self.message = "Error: Invalid arguments: " + self.d.bad_arguments
        self.number = 1


class ENone(ERootException):
    def __init__(self):
        self.message = "OK"
        self.number = 0


def PrintUsage():
    """ prints out usage information """

    print "PercolateTest.py"
    print "Processes a rolodex input file into JSON.\n"
    print "usage: PercolateTest.py <filename> [-v]"
    print "     filename = input file to parse. Output written to result.out"
    print "usage: PercolateTest.py -t <canonical input file prefix only>"
    print "     <canonical input file prefix only> eg 'canonical' uses canonical.in and canonical.out"
    print "usage: PercolateTest.py -t <canonical in> <canonical out>\n"
    print "-h usage"
    print "-t run in test mode (implies -v)"
    print "-v verbose output (normally off)"
    print "(note that data integrity checks are run on all input records whether in test mode or not)\n"
    print "returned errors:"
    print "0 - Completed OK"
    print "1 - No input file specified"
    print "2 - Specified file was not found"
    print "3 - Self test files not found after -t specified"
    print "4 - test using canonical data failed"
    print "5 - i/o error during input read\n"
    # True means function completed successfully
    raise ENone



def ProcessArgs(arglist):
    """     reads arguments and sets flags and variables
    :param arglist: list of arguments from command line
    :returns : tuple of all the flags and file names
    """
    global console_io
    global test_mode
    global verbose_mode
    global data_file_name
    global canonical_output_file

    data_file_name = None
    canonical_output_file = None

    verbose_mode = False
    test_mode = False
    console_io = False

    arglist.remove(arglist[0])
    if "-h" in arglist or arglist == []:
        try:
            PrintUsage()
        except ENone:
            pass
        raise ENone
    elif len(arglist) == 0:
        PrintUsage()
        raise EInvalidArguments(message="No arguments passed")
    elif "-t" in arglist:
        arglist.remove("-t")  # we know we're in test mode
        if "-v" in arglist:
            arglist.remove("-v")  # verbose will be true anyway
        if len(arglist) == 0:
            console_io = True
        if len(arglist) == 1:
            data_file_name = arglist[0] + ".in"  # test data
            canonical_output_file = arglist[0] + ".out"  # test data
        if len(arglist) == 2:
            data_file_name = arglist[0]  # test data
            canonical_output_file = arglist[1]  # test data
        if not console_io:
            if not os.path.isfile(data_file_name):
                raise EFileNotFound(filename="input file: " + data_file_name)
            if not os.path.isfile(canonical_output_file):
                raise EFileNotFound(filename="output file: " + canonical_output_file)
        test_mode = True
        verbose_mode = True
    else:
        if "-v" in arglist:
            verbose_mode = True
            arglist.remove("-v")
        data_file_name = arglist[0]
        # validate file
        if not os.path.isfile(data_file_name):
            raise EFileNotFound(message="input file:" + data_file_name)

    # return values can be used for testing
    raise ENone


def FetchNext():
    """ generator - returns next input line
    :var data_file_name (global): file to read
    :var console_io (global): flag which tells us "input file" vs "console input"
    :returns : raw_line from input stream
    """

    if console_io:
        for raw_line in sys.stdin:
            yield raw_line
    else:
        with open(data_file_name, 'r') as input_file_handle:
            for raw_line in input_file_handle:
                yield raw_line



filter_pattern = "[0-9a-zA-Z\s\-\.,]+"
refilter = re.compile(filter_pattern)


def RegexFilter(line):
    global refilter
    list_of_strings = refilter.findall(line)
    return ''.join(list_of_strings)



def NormalizeTheData(line):
    fields_temp = line.split(",")
    fields = []
    counter = 0
    for i in fields_temp:
        counter += 1
        i = i.strip()
        if counter > 2:
            i = i.replace(" ", "")
        fields.append(i)
    return fields


def BuildRecordList():
    """ heavy lifting = rules processing & data integrity checks """

    interim_list_of_records = []
    list_of_errors = []
    list_of_error_details = []

    record_number = -1
    try:
        # now process the file
        for raw_line in FetchNext():
            record_number += 1
            line = unicode(raw_line.strip())

            # rules
            # only lines with commas are good
            if "," not in line:
                list_of_errors.append(record_number)
                list_of_error_details.append({"record": record_number, "error": "nocomma", "line": raw_line})
                continue

            # regex filter to keep letters, numbers, commas, periods and spaces
            line = RegexFilter(line)

            # normalize the data
            fields = NormalizeTheData(line)

            # do we have enough fields
            number_of_fields = len(fields)
            if number_of_fields < 4 or number_of_fields > 5:
                list_of_errors.append(record_number)
                list_of_error_details.append({"record": record_number,
                                              "error": "wrong#fields:" + str(number_of_fields), "line": raw_line})
                continue

            # find the color to determine field order
            # and start building the new record
            if number_of_fields == 4:
                name = fields[0].split(" ")
                last = name[len(name)-1]
                name.remove(last)
                first = ' '.join(name)
                zip_code = fields[2]
                phone = fields[3]
                color = fields[1]
            elif not fields[4].isnumeric():
                first = fields[0]
                last = fields[1]
                zip_code = fields[2]
                phone = fields[3]
                color = fields[4]
            elif not fields[3].isnumeric():
                last = fields[0]
                first = fields[1]
                phone = fields[2]
                color = fields[3]
                zip_code = fields[4]
            else:
                list_of_errors.append(record_number)
                list_of_error_details.append({"record": record_number, "error": "nocolor", "line": raw_line})
                continue

            # unknown color?
            if color not in valid_colors:
                list_of_errors.append(record_number)
                list_of_error_details.append({"record": record_number, "error": "unkcolor: " + color, "line": raw_line})
                continue

            # invalid zip?
            if len(zip_code) > 5 or len(zip_code) < 5:
                list_of_errors.append(record_number)
                list_of_error_details.append({"record": record_number, "error": "badzip: " + zip_code, "line": raw_line})
                continue

            # invalid phone
            phone = phone.replace(" ", "")
            phone = phone.replace("-", "")
            if len(phone) > 10 or len(phone) < 7:
                list_of_errors.append(record_number)
                list_of_error_details.append({"record": record_number, "error": "badphone: " + phone, "line": raw_line})
                continue

            # package up the data for the next step
            new_record = (last + ", " + first,
                          {u"color": color, u"first": first, u"last": last, u"phone": phone, u"zip": zip_code})
            interim_list_of_records.append(new_record)

    except Exception as e:
        print
        sys.stderr.write("error - unknown input file error\n")
        sys.stderr.write("%s\n" % e)
        traceback.print_exc()
        sys.exit(5)

    # return values can be used for testing
    return interim_list_of_records, list_of_errors, list_of_error_details


def SortAndFinalize(interim_list_of_records, list_of_errors, list_of_error_details):
    """
    :param interim_list_of_records: list of records already generated
    :param list_of_errors:
    :param list_of_error_details:
    :return data: the JSON ready collection
    """
    # sort...
    interim_list_of_records.sort()
    list_of_records = []
    for item in interim_list_of_records:
        list_of_records.append(item[1])

    # finalize...
    if verbose_mode:
        data = {"entries": list_of_records, "errors": list_of_errors, "error_details": list_of_error_details}
    else:
        data = {"entries": list_of_records, "errors": list_of_errors}

    return data


def OutputResults(data):
    """ writes results
    :param data: the JSON ready data to write
    :var verbose_mode : tells the code to write to console too
    """
    global verbose_mode
    # output...
    with open('result.out', 'w') as output_file:
        json.dump(data, output_file, sort_keys=True, indent=2)

    if verbose_mode:
        print "json:\n", json.dumps(data, sort_keys=True, indent=2)


def ValidateFile():
    """ validates output to canonical file
    :var canonical_output_file : file name to compare with
    """
    if test_mode:
        if not filecmp.cmp('result.out', canonical_output_file):
            sys.stderr.write("error - canonical test output failed\n")
            sys.exit(4)
        print "Validation OK. %s == %s" % (data_file_name, canonical_output_file)


def percolate_main():
    print "Main start"
    try:
        ProcessArgs(sys.argv)
    except ENone:
        pass
    except ERootException as e:
        sys.stderr.write(e.message)
        sys.exit(e.number)
    try:
        interim_list_of_records, list_of_errors, list_of_error_details = BuildRecordList()
    except ENone:
        pass
    try:
        data = SortAndFinalize(interim_list_of_records, list_of_errors, list_of_error_details)
    except ENone:
        pass
    try:
        OutputResults(data)
    except ENone:
        pass
    try:
        ValidateFile()
    except ENone:
        pass
    print "Main complete"

if __name__ == '__main__':
    percolate_main()

#!/usr/bin/env python

# import re
# import sys
# from argparse import FileType

# import agate

from argparse import FileType
from sys import argv, stderr
import six
import warnings

from csvkit.grep import FilteringCSVReader

# from csvkit.cli import CSVKitUtility

from csvkit.utilities.csvgrep import CSVGrep
from csvkitcat import agate, parse_column_identifiers, rxlib as re




class CSVRgrep(CSVGrep):
    description = 'Like csvgrep, except with support for multiple expressions'
    override_flags = ['f', 'L', 'blanks', 'date-format', 'datetime-format']

    def add_arguments(self):
        def option_parser_flag(bytestring=None):
            if bytestring is None:
                return True
            elif six.PY2:
                return bytestring.decode(sys.getfilesystemencoding())
            else:
                return bytestring

        self.argparser.add_argument('-E', '--expr', dest='expressions_list', action='append',
                nargs='*',
                help='Store a list of patterns to match')

        # self.argparser.add_argument('-r', '--regex', dest='regex', action='store',

        #                             # type=option_parser_flag,
        #                             default=False,
        #                             nargs='?',
        #                             help='If specified, must be followed by a regular expression which will be tested against the specified columns.')

        self.argparser.add_argument('-m', '--literal-match', dest="literal_match", action='store_true',
                                    # type=option_parser_flag,
                                    default=False,
                                    # nargs='?',
                                    help='Match patterns literally instead of using regular expressions')

        self.argparser.add_argument('-n', '--names', dest='names_only', action='store_true',
                                    help='Display column names and indices from the input CSV and exit.')
        self.argparser.add_argument('-c', '--columns', dest='columns',
                                    help='A comma separated list of column indices, names or ranges to be searched, e.g. "1,id,3-5".')
        # self.argparser.add_argument('-m', '--match', dest="pattern", action='store', type=option_parser,
        #                             help='The string to search for.')
        # self.argparser.add_argument('-r', '--regex', dest='regex', action='store', type=option_parser,
        #                             help='If specified, must be followed by a regular expression which will be tested against the specified columns.')
        # self.argparser.add_argument('-f', '--file', dest='matchfile', type=FileType('r'), action='store',
        #                             help='If specified, must be the path to a file. For each tested row, if any line in the file (stripped of line separators) is an exact match for the cell value, the row will pass.')
        self.argparser.add_argument('-i', '--invert-match', dest='inverse', action='store_true',
                                    help='If specified, select non-matching instead of matching rows.')
        self.argparser.add_argument('-a', '--all-match', dest='all_match', action='store_true',
                                    help='If specified, only select rows for which every column matches the given pattern')


        self.argparser.add_argument(metavar='FILE', nargs='?', dest='input_path',
                                    help='The CSV file to operate on. If omitted, will accept input as piped data via STDIN.')




    def run(self):
        """
        A wrapper around the main loop of the utility which handles opening and
        closing files.
        """



        if not self.args.input_path:
            # then it must have been eaten by an -E flag; we assume the input file is in e[-1],
            # where `e` is the last member of expressions_list
            self.args.input_path = self.args.expressions_list[-1].pop()


        self.input_file = self._open_input_file(self.args.input_path)

        try:
            with warnings.catch_warnings():
                if getattr(self.args, 'no_header_row', None):
                    warnings.filterwarnings(action='ignore', message='Column names not specified', module='agate')

                self.main()
        finally:
            self.input_file.close()



    def main(self):
        if self.args.names_only:
            self.print_column_names()
            return

        if self.additional_input_expected():
            stderr.write('No input file or piped data provided. Waiting for standard input:\n')

        if not self.args.expressions_list:
            self.argparser.error('Must specify at least one -E/--expr expression')

        for i, e in enumerate(self.args.expressions_list):
            if len(e) == 0:
                self.argparser.error("-E requires at least 1 argument representing a pattern to be grepped")
            if len(e) > 2:
                self.argparser.error(f"""The #{i+1} invocation of -E had too many arguments (1 or 2 is expected): {e} """)

            if len(e) < 2:
                e.append('')




            # delattr(self.args, 'expressions_list')
            # vargs = self.args
            # vargs.pop('expressions_list')
            # _ipath = vargs.pop('input_path')

            # stdgrep = CSVGrep(argv[1:])
            # # stdgrep = CSVGrep(self.args)
            # return stdgrep.run()

        # if self.args.matchfile is not None:
        #     self.argparser.error('Cannot use -f/--matchfile and -E together')


        # if self.args.regex is False and self.args.pattern is False:
        #     self.argparser.error('Either -r or -m must be set')

        # for _name, _flag in (('regex','-r') , ('pattern','-m') ):
        #     _att = getattr(self.args, _name, False)
        #     if _att and not isinstance(_att, bool):
        #         self.argparser.error(f"In -E/--expr mode, {_flag} is just a flag – i.e. don't pass a value to it")

        self.all_match = self.args.all_match
        self.any_match = not self.all_match
        self.literal_match = self.args.literal_match

        reader_kwargs = self.reader_kwargs
        writer_kwargs = self.writer_kwargs
        # Move the line_numbers option from the writer to the reader.
        if writer_kwargs.pop('line_numbers', False):
            reader_kwargs['line_numbers'] = True

        rows, column_names, default_column_ids = self.get_rows_and_column_names_and_column_ids(**reader_kwargs)

        filtered_rows = rows

        for epat, ecols in self.args.expressions_list:
            if self.args.literal_match:
                pattern = epat
            else: # literal match
                pattern = re.compile(epat)

            if ecols:
                ecol_ids = parse_column_identifiers(ecols, column_names, self.get_column_offset(), getattr(self.args, 'not_columns', None))
            else:
                ecol_ids = default_column_ids

            epatterns = dict((eid, pattern) for eid in ecol_ids)


            filtered_rows = FilteringCSVReader(filtered_rows, header=False, patterns=epatterns,
                inverse=self.args.inverse, any_match=self.any_match)
            # o_reader = agate.csv.reader(self.skip_lines(), **reader_kwargs)
            # import IPython; IPython.embed()

            # for row in i_reader:
            #     o_reader.append(row)

            # i_rows = o_reader


        output = agate.csv.writer(self.output_file, **writer_kwargs)
        output.writerow(column_names)
        for row in filtered_rows:
            output.writerow(row)


        # if self.args.names_only:
        #     self.print_column_names()
        #     return

        # if self.additional_input_expected():
        #     sys.stderr.write('No input file or piped data provided. Waiting for standard input:\n')

        # # if not self.args.columns:
        # #     self.argparser.error('You must specify at least one column to search using the -c option.')



        # else:
        #     if self.args.matchfile is not None:
        #         self.argparser.error('Cannot use -m and -E together')
        #     # if self.args.regex is None and self.args.pattern is None:
        #     #     self.argparser.error('Either -')





        # reader_kwargs = self.reader_kwargs
        # writer_kwargs = self.writer_kwargs
        # # Move the line_numbers option from the writer to the reader.
        # if writer_kwargs.pop('line_numbers', False):
        #     reader_kwargs['line_numbers'] = True

        # rows, column_names, column_ids = self.get_rows_and_column_names_and_column_ids(**reader_kwargs)


        # self.grep_expressions = getattr(self.args, 'expressions_list', [])


        # if self.grep_expressions:


        # else:
        #     # standard behavior
        # if self.args.regex:
        #     pattern = re.compile(self.args.regex)
        # elif self.args.matchfile:
        #     lines = set(line.rstrip() for line in self.args.matchfile)
        #     self.args.matchfile.close()

        #     def pattern(x):
        #         return x in lines
        # else:
        #     pattern = self.args.pattern

        # patterns = dict((column_id, pattern) for column_id in column_ids)
        # filter_reader = FilteringCSVReader(rows, header=False, patterns=patterns, inverse=self.args.inverse, any_match=self.args.any_match)

        # output = agate.csv.writer(self.output_file, **writer_kwargs)
        # output.writerow(column_names)

        # for row in filter_reader:
        #     output.writerow(row)


def launch_new_instance():
    utility = CSVRgrep()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()

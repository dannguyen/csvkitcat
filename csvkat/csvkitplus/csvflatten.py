#!/usr/bin/env python


"""
Example usage:

    $ csvflatten examples/longvals.csv --max-length 50 | csvlook


Output:

    | header       | value                                              |
    | ------------ | -------------------------------------------------- |
    | title        | Raising Arizona                                    |
    | release_date | March 13, 1987                                     |
    | length       | 94                                                 |
    | box_office   | 292000000                                          |
    | description  | Repeat convict "Hi" and police officer "Ed" meet i |
    |              | n prison, get married, and hope to raise a family. |
    | url          | https://en.wikipedia.org/wiki/Raising_Arizona      |


TODOS:

- write tests
- how does typecasted values work?
- any need to remove unnecessary arguments from base CSVKitUtility?
- why do I have to set quote mode to 1 when working with examples/longvals.csv?
- add flag to do max-length record breaking, but in newline mode (e.g. ideal for spreadsheets)
- make sure 2.x and 3.x compatible
"""

import agate
from csvkit.cli import CSVKitUtility
import re
import sys

OUTPUT_COLUMNS = {'names': ['header', 'value',], 'types': (agate.Text(), agate.Text())}
DEFAULT_NEW_RECORD_MARKER = '~#####'

class CSVFlatten(CSVKitUtility):
    description = """Prints flattened records, such that each row represents a record's header and corresponding value,
                     similar to transposing a record in spreadsheet format"""

    override_flags = ['L', 'blanks', 'date-format', 'datetime-format']


    def add_arguments(self):
        self.argparser.add_argument('--marker', dest='new_record_marker', type=str,
                                    default=DEFAULT_NEW_RECORD_MARKER,
                                    help="""When flattening multiple records, separate each records with a row w/ header of [marker].
                                            Set to '' or 'false' or 'none' to disable""")
        self.argparser.add_argument('--max-length', dest='max_value_length', type=int,
                                    help="""Chop up values to fit this length; longer values are split into multiple rows,
                                             e.g. for easier viewing when passing into csvlook""")

        self.argparser.add_argument('-D', '--out-delimiter', dest='out_delimiter',
                                    help='Delimiting character of the output CSV file.')
        self.argparser.add_argument('-T', '--out-tabs', dest='out_tabs', action='store_true',
                                    help='Specify that the output CSV file is delimited with tabs. Overrides "-D".')
        self.argparser.add_argument('-Q', '--out-quotechar', dest='out_quotechar',
                                    help='Character used to quote strings in the output CSV file.')
        self.argparser.add_argument('-U', '--out-quoting', dest='out_quoting', type=int, choices=[0, 1, 2, 3], default=1,
                                    help='Quoting style used in the output CSV file. 0 = Quote Minimal, 1 = Quote All, 2 = Quote Non-numeric, 3 = Quote None.')
        self.argparser.add_argument('-B', '--out-no-doublequote', dest='out_doublequote', action='store_false',
                                    help='Whether or not double quotes are doubled in the output CSV file.')
        self.argparser.add_argument('-P', '--out-escapechar', dest='out_escapechar',
                                    help='Character used to escape the delimiter in the output CSV file if --quoting 3 ("Quote None") is specified and to escape the QUOTECHAR if --no-doublequote is specified.')
        self.argparser.add_argument('-M', '--out-lineterminator', dest='out_lineterminator',
                                    help='Character used to terminate lines in the output CSV file.')


    def _extract_csv_writer_kwargs(self):
        kwargs = {}

        # if self.args.line_numbers:
        #     kwargs['line_numbers'] = True

        if self.args.out_tabs:
            kwargs['delimiter'] = '\t'
        elif self.args.out_delimiter:
            kwargs['delimiter'] = self.args.out_delimiter

        for arg in ('quotechar', 'quoting', 'doublequote', 'escapechar', 'lineterminator'):
            value = getattr(self.args, 'out_%s' % arg)
            if value is not None:
                kwargs[arg] = value

        return kwargs


    def _figure_out_record_marker(self):
        x = self.args.new_record_marker
        if not x or x in ('none', 'false'):
            self.new_record_marker = None
        else:
            self.new_record_marker = x

    def main(self):
        if self.additional_input_expected():
            self.argparser.error('You must provide an input file or piped data.')

        self._figure_out_record_marker()

        raw_rows = agate.csv.reader(self.skip_lines(), **self.reader_kwargs)
        raw_column_names = next(raw_rows)


        writer = agate.csv.writer(self.output_file, **self.writer_kwargs)
        writer.writerow(OUTPUT_COLUMNS['names'])
        maxvallength = self.args.max_value_length

        for y, row in enumerate(raw_rows):
            if self.new_record_marker and y > 0:
                # a "normal" header/value row, in which value is less than maxcolwidth
                writer.writerow((self.new_record_marker, None))

            for x, header in enumerate(raw_column_names):
                value = row[x]
                lenval = len(value)
                if not maxvallength or maxvallength >= lenval:
                    writer.writerow([header, value])
                else:
                    # if value is longer than max_value_length,
                    # we split the value into chunks of max_value_length
                    # and output a new row for each chunk as the value, and None for the header
                    for i in range(0, lenval, maxvallength):
                        chunk = value[i:i+maxvallength]
                        header = header if i == 0 else None
                        writer.writerow([header, chunk])




def launch_new_instance():
    utility = CSVFlatten()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()

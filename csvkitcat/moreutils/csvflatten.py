#!/usr/bin/env python

import agate
from csvkit.cli import CSVKitUtility
import regex as re
import sys

OUTPUT_COLUMNS = {'names': ['fieldname', 'value',], 'types': (agate.Text(), agate.Text())}
DEFAULT_EOR_MARKER = '~~~~~~~~~'

class CSVFlatten(CSVKitUtility):
    description = """Prints flattened records, such that each row represents a record's fieldname and corresponding value,
                     similar to transposing a record in spreadsheet format"""

    override_flags = ['L', 'blanks', 'date-format', 'datetime-format']


    def add_arguments(self):
        self.argparser.add_argument('-X', '--chop-x', dest='chop_length', type=int,
                                    help="""Chop up values to fit this length; longer values are split into multiple rows,
                                             e.g. for easier viewing when passing into csvlook. Note that this forces
                                             the option --out-quoting=1""")

        self.argparser.add_argument('--chop-labels', dest='label_chopped_values',
                                    action='store_true',
                                    help="""When a value is chopped into multiple rows, the `fieldname` (i.e. first column)
                                            is left blank after the first chop/row. Setting the --X-label flag
                                            will fill the `fieldname` column with: "fieldname~n", where `n` indicates
                                            the n-th row of a chopped value""")

        self.argparser.add_argument('--eor', dest='end_of_record_marker', type=str,
                                    default=DEFAULT_EOR_MARKER,
                                    help="""end of record; When flattening multiple records, separate each records with
                                            a row w/ fieldname of [marker]. Set to '' or 'none' to disable""")

        self.argparser.add_argument('-D', '--out-delimiter', dest='out_delimiter',
                                    help='Delimiting character of the output CSV file.')
        self.argparser.add_argument('-T', '--out-tabs', dest='out_tabs', action='store_true',
                                    help='Specify that the output CSV file is delimited with tabs. Overrides "-D".')
        self.argparser.add_argument('-Q', '--out-quotechar', dest='out_quotechar',
                                    help='Character used to quote strings in the output CSV file.')
        self.argparser.add_argument('-U', '--out-quoting', dest='out_quoting', type=int, choices=[0, 1, 2, 3],
                                    help='Quoting style used in the output CSV file. 0 = Quote Minimal, 1 = Quote All, 2 = Quote Non-numeric, 3 = Quote None.')
        self.argparser.add_argument('-B', '--out-no-doublequote', dest='out_doublequote', action='store_false',
                                    help='Whether or not double quotes are doubled in the output CSV file.')
        self.argparser.add_argument('-P', '--out-escapechar', dest='out_escapechar',
                                    help='Character used to escape the delimiter in the output CSV file if --quoting 3 ("Quote None") is specified and to escape the QUOTECHAR if --no-doublequote is specified.')
        self.argparser.add_argument('-M', '--out-lineterminator', dest='out_lineterminator',
                                    help='Character used to terminate lines in the output CSV file.')

        # TODO
        # self.argparser.add_argument('-y', '--snifflimit', dest='sniff_limit', type=int,
        #                             help='Limit CSV dialect sniffing to the specified number of bytes. Specify "0" to disable sniffing entirely.')
        # self.argparser.add_argument('-I', '--no-inference', dest='no_inference', action='store_true',
        #                             help='Disable type inference when parsing the input.')



    def _extract_csv_writer_kwargs(self):
        kwargs = {}

        # if self.args.line_numbers:
        #     kwargs['line_numbers'] = True

        if self.args.out_tabs:
            kwargs['delimiter'] = '\t'
        elif self.args.out_delimiter:
            kwargs['delimiter'] = self.args.out_delimiter

        if self.args.chop_length:
            # we force arg.out_quoting to be 1 i.e. Quote All
            self.args.out_quoting = 1



        for arg in ('quotechar', 'quoting', 'doublequote', 'escapechar', 'lineterminator'):
            value = getattr(self.args, 'out_%s' % arg)
            if value is not None:
                kwargs[arg] = value


        return kwargs


    def _figure_out_record_marker(self):
        x = self.args.end_of_record_marker
        if not x or x in ('none', 'false'):
            self.end_of_record_marker = None
        else:
            self.end_of_record_marker = x

    def main(self):
        if self.additional_input_expected():
            self.argparser.error('You must provide an input file or piped data.')

        self._figure_out_record_marker()

        raw_rows = agate.csv.reader(self.skip_lines(), **self.reader_kwargs)
        raw_column_names = next(raw_rows)


        writer = agate.csv.writer(self.output_file, **self.writer_kwargs)
        writer.writerow(OUTPUT_COLUMNS['names'])
        maxvallength = self.args.chop_length
        if maxvallength:
            valpattern = re.compile(fr'[^\n]{{{maxvallength}}}|.+?(?=\n|$)')
        else:
            valpattern = re.compile(r'.+?(?=\n|$)')


        for y, row in enumerate(raw_rows):
            if self.end_of_record_marker and y > 0:
                # a "normal" fieldname/value row, in which value is less than maxcolwidth
                writer.writerow((self.end_of_record_marker, None))

            for x, fieldname in enumerate(raw_column_names):
                value = row[x]
                lenval = len(value)
                # if not maxvallength or maxvallength >= lenval:
                #     writer.writerow([fieldname, value])
                # else:
                    # if value is longer than chop_length,
                    # we split the value into chunks of chop_length
                    # and output a new row for each chunk as the value, and None for the fieldname
                chunks = valpattern.findall(value)
                for i, chunk in enumerate(chunks):
                    if i == 0:
                        fname = fieldname
                    elif self.args.label_chopped_values is True:
                        fname = f'{fieldname}~{i}'
                    else:
                        fname = None
                    writer.writerow([fname, chunk])


                    # for _n, z in enumerate(range(0, lenval, maxvallength)):
                    #     chunk = value[z:z+maxvallength]
                    #     if _n == 0:
                    #         fname = fieldname
                    #     elif self.args.label_chopped_values is True:
                    #         fname = f'{fieldname}~{_n}'
                    #     else:
                    #         fname = None
                    #     writer.writerow([fname, chunk])




def launch_new_instance():
    utility = CSVFlatten()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()

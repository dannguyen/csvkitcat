#!/usr/bin/env python

from csvkitcat import agate, CSVKitUtility
from csvkitcat import rxlib as re
import sys

OUTPUT_COLUMNS = {'names': ['fieldname', 'value',], 'types': (agate.Text(), agate.Text())}
DEFAULT_EOR_MARKER = '~~~~~~~~~'

class CSVFlatten(CSVKitUtility):
    description = """Prints flattened records, such that each row represents a record's fieldname and corresponding value,
                     similar to transposing a record in spreadsheet format"""

    override_flags = ['l', 'L', 'blanks', 'date-format', 'datetime-format']


    def add_arguments(self):
        self.argparser.add_argument('-L', '--chop-length', dest='chop_length', type=int,
                                    help="""Chop up values to fit this length; longer values are split into multiple rows,
                                             e.g. for easier viewing when passing into csvlook. Note that this forces
                                             the option --out-quoting=1""")

        self.argparser.add_argument('-B', '--chop-labels', dest='label_chopped_values',
                                    action='store_true',
                                    help="""When a value is chopped into multiple rows, the `fieldname` (i.e. first column)
                                            is left blank after the first chop/row. Setting the --X-label flag
                                            will fill the `fieldname` column with: "fieldname~n", where `n` indicates
                                            the n-th row of a chopped value""")

        self.argparser.add_argument('-E', '--eor', dest='end_of_record_marker', type=str,
                                    default=DEFAULT_EOR_MARKER,
                                    help="""end of record; When flattening multiple records, separate each records with
                                            a row w/ fieldname of [marker]. Set to '' or 'none' to disable""")


    def _extract_csv_writer_kwargs(self):
        kwargs = {}

        if self.args.chop_length:
            # we force arg.out_quoting to be 1 i.e. Quote All
            kwargs['quoting'] = self.args.out_quoting = 1


        return kwargs


    def _figure_out_record_marker(self):
        x = self.args.end_of_record_marker
        if not x or x in ('none',):
            self.end_of_record_marker = None
        else:
            self.end_of_record_marker = x

    def main(self):
        if self.additional_input_expected():
            self.argparser.error('You must provide an input file or piped data.')


        if self.args.label_chopped_values and not self.args.chop_length:
            self.argparser.error('"-B/--chop-label is an invalid option unless -L/--chop-length is specified')

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

                chunks = valpattern.findall(value)
                for i, chunk in enumerate(chunks):
                    if i == 0:
                        fname = fieldname
                    elif self.args.label_chopped_values is True:
                        fname = f'{fieldname}~{i}'
                    else:
                        fname = None
                    writer.writerow([fname, chunk])





def launch_new_instance():
    utility = CSVFlatten()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()

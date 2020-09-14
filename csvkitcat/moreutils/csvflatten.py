#!/usr/bin/env python

from csvkitcat.kitcat.justtext import JustTextUtility
from csvkitcat import agate
from csvkitcat import rxlib as re
import sys

FLAT_COLUMNS = {'names': ['fieldname', 'value',], 'types': (agate.Text(), agate.Text())}
DEFAULT_EOR_MARKER = '~~~~~~~~~'

class CSVFlatten(JustTextUtility):
    description = """Prints flattened records, such that each row represents a record's fieldname and corresponding value,
                     similar to transposing a record in spreadsheet format"""

    override_flags = ['L', 'blanks', 'date-format', 'datetime-format']


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
        kwargs = super()._extract_csv_writer_kwargs()

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

        maxvallength = self.args.chop_length
        if maxvallength:
            valpattern = re.compile(fr'[^\n]{{1,{maxvallength}}}')
        else:
            valpattern = re.compile(r'.+')


        myio = self.init_io(write_header=False)
        myio.output.writerow(FLAT_COLUMNS['names'])


        for y, row in enumerate(myio.rows):
            if self.end_of_record_marker and y > 0:
                # a "normal" fieldname/value row, in which value is less than maxcolwidth
                myio.output.writerow((self.end_of_record_marker, None))

            for x, fieldname in enumerate(myio.column_names):
                linevalues = row[x].strip().splitlines()
                _linecount = 0
                for i, value in enumerate(linevalues):
                    if not value: # i.e. a blank new line
                        _linecount += 1
                        fname = f'{fieldname}~{_linecount}' if self.args.label_chopped_values is True else None
                        myio.output.writerow([fname, ""])
                    else:
                        chunks = valpattern.findall(value)
                        for j, chunk in enumerate(chunks):
                            if _linecount == 0:
                               fname = fieldname
                            else:
                                fname = f'{fieldname}~{_linecount}' if self.args.label_chopped_values is True else None
                            _linecount += 1
                            myio.output.writerow([fname, chunk])




def launch_new_instance():
    utility = CSVFlatten()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()

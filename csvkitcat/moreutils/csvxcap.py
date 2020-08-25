#!/usr/bin/env python

from csvkitcat.alltext import AllTextUtility
from csvkitcat.exceptions import ArgumentErrorTK
import regex as re
import warnings

DEFAULT_COL_PREFIX = 'xcap'

class CSVXcap(AllTextUtility):
    description = """Capture regex groups in [COLUMN] with [PATTERN] and create new columns"""

    override_flags = ['f', 'S', 'L', 'blanks', 'date-format', 'datetime-format']



    def add_arguments(self):


        self.argparser.add_argument(metavar='COLUMN', dest='target_column',
                                    help='A column to split by pattern')

        self.argparser.add_argument(metavar='PATTERN', dest='pattern',
                                    help='A regex pattern to split by')


        self.argparser.add_argument(metavar='FILE', nargs='?', dest='input_path',
                                    help='The CSV file to operate on. If omitted, will accept input as piped data via STDIN.')




    def run(self):
        """
        A wrapper around the main loop of the utility which handles opening and
        closing files.

        TK: This is copy-pasted form CSVKitUtil because we have to override 'f'; maybe there's
            a way to refactor this...
        """
        self.input_file = self._open_input_file(self.args.input_path)

        try:
            with warnings.catch_warnings():
                if getattr(self.args, 'no_header_row', None):
                    warnings.filterwarnings(action='ignore', message='Column names not specified', module='agate')

                self.main()
        finally:
            self.input_file.close()


    def main(self):

        if self.additional_input_expected():
            self.argparser.error('You must provide an input file or piped data.')

        self.args.columns = self.args.target_column
        myio = self.init_io(write_header=False)

        if len(myio.column_ids) != 1:
            raise ArgumentErrorTK(f"[COLUMN] argument expects exactly one column identifier, not {len(myio.column_ids)} columns: {myio.column_names}")

        x_cid = myio.column_ids[0]
        x_cname = myio.column_names[x_cid]

        pattern = re.compile(self.args.pattern)

        if pattern.groups == 0:
            # regex contains no capturing groups, so just one new column
            # is created with a generic name
            n_xcols = 1
            xcol_names = [f'{x_cname}_{DEFAULT_COL_PREFIX}']
        elif pattern.groupindex:
            # i.e. has named  captured groups
            n_xcols = len(pattern.groupindex)
            xcol_names = [f'{x_cname}_{k}' for k in pattern.groupindex.keys()]
        else:
            # just regular captured groups
            n_xcols = pattern.groups
            xcol_names = [f'{x_cname}_{DEFAULT_COL_PREFIX}{i+1}' for i in range(n_xcols)]


        new_fieldnames = myio.column_names + xcol_names

        myio.output.writerow(new_fieldnames)

        for row in myio.rows:
            xval = row[x_cid]
            # print('xval', xval)
            rxmatch = pattern.search(xval)
            if not rxmatch:
                newvals = [None for i in range(n_xcols)]
            elif not rxmatch.groups():
                # just a single pattern match, no capture group
                newvals = [rxmatch.group()]
            else:
                newvals = rxmatch.groups()

            row.extend(newvals)
            myio.output.writerow(row)


def launch_new_instance():
    utility = CSVXcap()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()

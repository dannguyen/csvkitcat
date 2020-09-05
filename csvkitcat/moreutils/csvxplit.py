#!/usr/bin/env python

from csvkitcat.alltext import AllTextUtility
from csvkitcat.exceptions import ArgumentErrorTK
from csvkitcat import rxlib as re

import warnings

DEFAULT_COL_PREFIX = 'xp'

class CSVXplit(AllTextUtility):
    description = """Split a [COLUMN] by [PATTERN]"""

    override_flags = ['f', 'S', 'L', 'blanks', 'date-format', 'datetime-format']



    def add_arguments(self):

        self.argparser.add_argument('-r', '--regex', dest="regex_match", action='store_true',
                                    default=False,
                                    help='By default, [PATTERN] is assumed to be a regex. Set this flag to make it a literal text find/replace',)


        self.argparser.add_argument('-n', dest="n_split_count", action='store',
                                    default=1,
                                    type=int,
                                    help='Max number of splits to make')


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


        n_split_count = self.args.n_split_count
        pattern = self.args.pattern

        if self.args.n_split_count < 1:
            raise ArgumentErrorTK(f"The number of splits must be greater or equal to 1, not: {n_split_count}")


        self.args.columns = self.args.target_column
        myio = self.init_io(write_header=False)

        if len(myio.column_ids) != 1:
            raise ArgumentErrorTK(f"[COLUMN] argument expects exactly one column identifier, not {len(myio.column_ids)} columns: {myio.column_names}")

        column_id_to_split = myio.column_ids[0]
        column_name_to_split = myio.column_names[column_id_to_split]

        n_cols = n_split_count + 1
        split_column_names = [f'{column_name_to_split}_{DEFAULT_COL_PREFIX}{i}' for i in range(n_cols)]

        new_fieldnames = myio.column_names + split_column_names

        myio.output.writerow(new_fieldnames)

        for row in myio.rows:
            xval = row[column_id_to_split]
            # print('xval', xval)
            newvals = re.split(pattern, xval, n_split_count) if self.args.regex_match else xval.split(pattern, n_split_count)
            _lenvals = len(newvals)
            newvals = [newvals[i] if i < _lenvals else None for i in range(n_cols)]
            # print("Row:", row)
            # print("Newvals:", newvals)
            row.extend(newvals)

            myio.output.writerow(row)


def launch_new_instance():
    utility = CSVXplit()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()

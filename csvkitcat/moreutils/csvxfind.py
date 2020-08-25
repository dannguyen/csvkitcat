#!/usr/bin/env python

from csvkitcat.alltext import AllTextUtility
from csvkitcat.exceptions import ArgumentErrorTK
import regex as re
import warnings

DEFAULT_COL_PREFIX = 'xfind'
DEFAULT_XFIND_DELIMITER = ';'

class CSVXfind(AllTextUtility):
    description = """Find all regex [PATTERN] in [COLUMN], create new column with all matches"""

    override_flags = ['f', '-D', 'S', 'L', 'blanks', 'date-format', 'datetime-format']



    def add_arguments(self):


        self.argparser.add_argument(metavar='COLUMN', dest='target_column',
                                    help='A column to split by pattern')

        self.argparser.add_argument(metavar='PATTERN', dest='pattern',
                                    help='A regex pattern to split by')


        self.argparser.add_argument(metavar='FILE', nargs='?', dest='input_path',
                                    help='The CSV file to operate on. If omitted, will accept input as piped data via STDIN.')

        self.argparser.add_argument('-D', '--matches-delimiter', dest='xfind_delimiter',
                type=str,
                default=DEFAULT_XFIND_DELIMITER,
                help="The delimiter to use to separate any found matches",)


        self.argparser.add_argument('-n', '--first-n-matches', dest="n_matches", action='store',
                                    default=0,
                                    type=int,
                                    help='Max number of matches to find. If 0, then grab all the matches')




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
        x_delimiter = self.args.xfind_delimiter
        n_matches = self.args.n_matches if self.args.n_matches != 0 else None

        # only one column to create
        xcol_name = f'{x_cname}_{DEFAULT_COL_PREFIX}'

        new_fieldnames = myio.column_names + [xcol_name]

        myio.output.writerow(new_fieldnames)

        for row in myio.rows:
            xval = row[x_cid]
            matches = pattern.findall(xval)
            if not matches:
                newval = None
            else:
                newval = x_delimiter.join(matches[0:n_matches])

            row.append(newval)
            myio.output.writerow(row)


def launch_new_instance():
    utility = CSVXfind()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()

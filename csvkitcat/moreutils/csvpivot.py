import regex as re
from sys import stderr
import warnings

from csvkitcat import agate, CSVKitUtility
from csvkitcat.exceptions import ArgumentErrorTK



class CSVPivot(CSVKitUtility):
    description = """Do a simple pivot table, by row, column, or row and column"""

    override_flags = [ 'L', 'blanks', 'date-format', 'datetime-format']


    def add_arguments(self):
        self.argparser.add_argument('-n', '--names', dest='names_only', action='store_true',
                                    help='Display column names and indices from the input CSV and exit.')

        self.argparser.add_argument('-r', '--row-pivot', dest='row_pivot',
                                    type=str,
                                    help='TK row val pivot')

        self.argparser.add_argument('-c', '--column-pivot', dest='column_pivot',
                                    type=str,
                                    help='TK column val pivot',
                                    )

        self.argparser.add_argument('-y', '--snifflimit', dest='sniff_limit', type=int,
                                    help='Limit CSV dialect sniffing to the specified number of bytes. Specify "0" to disable sniffing entirely.')
        self.argparser.add_argument('-I', '--no-inference', dest='no_inference', action='store_true',
                                    help='Disable type inference when parsing the input.')


    def main(self):
        if self.additional_input_expected():
            self.argparser.error('You must provide an input file or piped data.')

        if self.args.names_only:
            self.print_column_names()
            return

        if not self.args.row_pivot and not self.args.column_pivot:
            raise ArgumentErrorTK('At least either --row-pivot or --column-pivot must be specified. Both cannot be empty' )

        table = agate.Table.from_csv(
            self.input_file,
            skip_lines=self.args.skip_lines,
            sniff_limit=self.args.sniff_limit,
            **self.reader_kwargs
        )

        pivot = table.pivot(key=self.args.row_pivot, pivot=self.args.column_pivot)

        pivot.to_csv(self.output_file, **self.writer_kwargs)


def launch_new_instance():
    utility = CSVPivot()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()

import csv
from io import StringIO
import regex as re
from sys import stderr
import warnings

from agate.aggregations import Count, Min, Max, MaxLength, Mean, Median, Mode, StDev, Sum


from csvkitcat import agate, parse_column_identifiers
from csvkitcat.agatable import AgatableUtil
from csvkitcat.exceptions import ArgumentErrorTK


PivotAggs = (Count, Max, MaxLength, Min, Mean, Median, Mode, StDev, Sum)


def get_agg(name: str) -> [type, bool]:
    return next((a for a in PivotAggs if a.__name__.lower() == name.lower()), False)

def parse_csv_line(line:str) -> list:
    """cmon, this must already be implemented in csvkit/agate somewhere..."""
    src = StringIO(line)
    return next(csv.reader(src), [])


class CSVPivot(AgatableUtil):
    description = """Do a simple pivot table, by row, column, or row and column"""

    override_flags = [ 'L', 'blanks', 'date-format', 'datetime-format']


    def add_arguments(self):
        self.argparser.add_argument('-n', '--names', dest='names_only', action='store_true',
                                    help='Display column names and indices from the input CSV and exit.')

        self.argparser.add_argument('-r', '--pivot-rows', dest='pivot_rows',
                                    type=str,
                                    help="""The column name(s) on which to use as pivot rows. Should be either one name
                                    (or index) or a comma-separated list with one name (or index)""")

        self.argparser.add_argument('-a', '--agg', dest='pivot_agg', type=str,
                                    default='count',
                                    help="""The name of an aggregation to perform on each group of data in the pivot table.
                                    For aggregations that require an argument (i.e. a column name), pass in a comma-delimited
                                    string, e.g. `-a "sum,age"

                                    """)

        self.argparser.add_argument('-c', '--pivot-column', dest='pivot_column',
                                    type=str,
                                    help='The column name/id to use as a pivot column. Only one is allowed',
                                    )

        self.argparser.add_argument('-y', '--snifflimit', dest='sniff_limit', type=int,
                                    help='Limit CSV dialect sniffing to the specified number of bytes. Specify "0" to disable sniffing entirely.')
        self.argparser.add_argument('-I', '--no-inference', dest='no_inference', action='store_true',
                                    help='Disable type inference when parsing the input.')


    def handle_standard_args(self):
        if self.additional_input_expected():
            self.argparser.error('You must provide an input file or piped data.')

        if self.args.names_only:
            self.print_column_names()
            return

        if not self.args.pivot_rows and not self.args.pivot_column:
            raise ArgumentErrorTK('At least either --row-pivot or --column-pivot must be specified. Both cannot be empty' )


    def main(self):

        if not self.args.pivot_agg:
            # then print list of aggregates
            self.output_file.write(f"List of aggregate functions:\n")
            for a in PivotAggs:
                self.output_file.write(f"- {a.__name__.lower()}\n")
            return
        else:
            agg_name, *agg_args = parse_csv_line(self.args.pivot_agg)
            pivot_agg = get_agg(agg_name)
            if pivot_agg is False:
                raise ArgumentErrorTK(f'Invalid aggregation: "{self.args.pivot_agg}". Call -a/--agg without a value to get a list of available aggregations')
            else:
                pivot_agg = pivot_agg(*agg_args)


        self.handle_standard_args()

        agtable = agate.Table.from_csv(
            self.input_file,
            skip_lines=self.args.skip_lines,
            sniff_limit=self.args.sniff_limit,
            **self.reader_kwargs
        )
        column_names = agtable.column_names

        _prow_ids = parse_column_identifiers(
            self.args.pivot_rows,
            column_names,
            column_offset=1,  # TK, do I need to worry about this?
            excluded_columns=getattr(self.args, 'not_columns', None)
        ) if self.args.pivot_rows else None
        pivot_row_names = [column_names[i] for i in _prow_ids] if _prow_ids else None

        _pcol_ids = parse_column_identifiers(
            self.args.pivot_column,
            column_names,
            column_offset=1,  # TK, do I need to worry about this?
            excluded_columns=getattr(self.args, 'not_columns', None)
        ) if self.args.pivot_column else None

        if _pcol_ids and len(_pcol_ids) > 1:
            raise ArgumentErrorTK(f'Only one --pivot-column is allowed, not {len(_pcol_ids)}: {_pcol_ids}' )
        else:
            pivot_col_name = column_names[_pcol_ids[0]] if _pcol_ids else None
        # print(f"{column_names=}")
        # print(f"{pivot_col_name=}\n{pivot_row_names=}")
        pivot = agtable.pivot(key=pivot_row_names, pivot=pivot_col_name, aggregation=pivot_agg)
        pivot.to_csv(self.output_file, **self.writer_kwargs)


def launch_new_instance():
    utility = CSVPivot()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()

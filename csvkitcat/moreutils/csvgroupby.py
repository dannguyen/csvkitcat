import csv
from io import StringIO

import regex as re
from sys import stderr
from typing import NoReturn
import warnings

from agate.aggregations import Count, Min, Max, MaxLength, Mean, Median, Mode, StDev, Sum


from csvkitcat import agate, parse_column_identifiers
from csvkitcat.agatable import AgatableUtil
from csvkitcat.exceptions import ArgumentErrorTK


GroupbyAggs = (Count, Max, MaxLength, Min, Mean, Median, Mode, StDev, Sum)


def get_agg(name: str) -> [type, bool]:
    return next((a for a in GroupbyAggs if a.__name__.lower() == name.lower()), False)

def parse_csv_line(line:str) -> list:
    """cmon, this must already be implemented in csvkit/agate somewhere..."""
    src = StringIO(line)
    return next(csv.reader(src), [])


class CSVGroupby(AgatableUtil):
    description = """Do the equivalent of a SQL group by"""

    override_flags = [ 'L', 'blanks', 'date-format', 'datetime-format']


    def add_arguments(self):
        self.argparser.add_argument('-n', '--names', dest='names_only', action='store_true',
                                    help='Display column names and indices from the input CSV and exit.')


        self.argparser.add_argument('-c', '--columns', dest='columns',
                                    type=str,
                                    help="The column/list of columns (comma-separated) to group by",
                                    )

        self.argparser.add_argument('-a', '--aggs', dest='aggregates', type=str,
                                    default='count',
                                    help="""
                                      The aggregate function/list of agg functions (comma-separated) to use on the grouped columns.
                                      Invoke `-a/--aggs` without an argument to see list of supported aggregate functions.
                                    """)


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

        if not self.args.columns:
            raise ArgumentErrorTK('At least one column must be specified with -c/--columns' )

    def handle_aggregate_args(self) -> [type, NoReturn]:
        if not self.args.aggregates:
            # then print list of aggregates
            self.output_file.write(f"List of aggregate functions:\n")
            for a in GroupbyAggs:
                self.output_file.write(f"- {a.__name__.lower()}\n")
            return
        else:
            return Count
            # agg_name, *agg_args = parse_csv_line(self.args.aggregates)
            # pivot_agg = get_agg(agg_name)
            # if pivot_agg is False:
            #     raise ArgumentErrorTK(f'Invalid aggregation: "{self.args.aggregates}". Call -a/--agg without a value to get a list of available aggregations')
            # else:
            #     pivot_agg = pivot_agg(*agg_args)
            #     return pivot_agg



    def main(self):
        self.handle_standard_args()
        self.aggregates = self.handle_aggregate_args()

        rawtable = agate.Table.from_csv(
            self.input_file,
            skip_lines=self.args.skip_lines,
            sniff_limit=self.args.sniff_limit,
            **self.reader_kwargs
        )
        column_names = rawtable.column_names

        _gcol_ids = parse_column_identifiers(
            self.args.columns,
            column_names,
            column_offset=1,  # TK, do I need to worry about this?
            excluded_columns=getattr(self.args, 'not_columns', None)
        )
        group_colnames = [column_names[i] for i in _gcol_ids]

        # outtable = rawtable.group_by(key=pivot_row_names, pivot=pivot_col_name, aggregation=pivot_agg)

        gtable = rawtable
        for col in group_colnames:
            gtable = gtable.group_by(key=col)


        gtable = gtable.aggregate([('Count', Count()),])

        gtable.to_csv(self.output_file, **self.writer_kwargs)


def launch_new_instance():
    utility = CSVGroupby()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()

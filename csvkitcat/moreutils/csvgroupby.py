import csv
from io import StringIO

import regex as re
from sys import stderr
from typing import NoReturn
import warnings



from csvkitcat import agate, parse_column_identifiers, slugify
from csvkitcat.agatable import AgatableUtil, parse_aggregate_string_arg, print_available_aggregates
from csvkitcat.exceptions import ArgumentErrorTK



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

        self.argparser.add_argument('-a', '--aggs', dest='aggregates',
                                    action='append',
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

    def handle_aggregate_args(self, valid_columns) -> [list, NoReturn]:
        """
        returns list of tuples, each tuple is: (Aggregate(*args), agg_column_name)
        """
        if not self.args.aggregates:
            # because we can't set default list in append action
            # https://bugs.python.org/issue16399
            self.args.aggregates = ['count']


        aggs = [parse_aggregate_string_arg(a, valid_columns) for a in self.args.aggregates]
        return aggs



    def main(self):
        if self.args.aggregates == ['list'] or self.args.aggregates == ['']:
            print_available_aggregates(self.output_file)
            return

        self.handle_standard_args()

        rawtable = agate.Table.from_csv(
            self.input_file,
            skip_lines=self.args.skip_lines,
            sniff_limit=self.args.sniff_limit,
            **self.reader_kwargs
        )
        column_names = rawtable.column_names

        self.aggregates = self.handle_aggregate_args(valid_columns=column_names)


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

        g_aggs = []
        for a in self.aggregates:
            if a.colname:
                colname = a.colname
            else:
                if a.args:
                    colname = f'{a.foo.__name__}_of_{slugify(a.args)}'
                else:
                    colname = a.foo.__name__
            agg = a.foo(*a.args)
            g_aggs.append((colname, agg))


        xtable = gtable.aggregate(g_aggs)
        xtable.to_csv(self.output_file, **self.writer_kwargs)

def launch_new_instance():
    utility = CSVGroupby()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()

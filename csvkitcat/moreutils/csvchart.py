import argparse
import warnings

from csvkitcat import agate, parse_column_identifiers
from csvkitcat.agatable import AgatableUtil
from csvkitcat.exceptions import ArgumentErrorTK
from csvkitcat.pandashelper import agate_to_df


import altair_viewer as altview
import altair as alt


def custom_init_common_parser(cparser):

    cparser.add_argument(metavar='FILE', nargs='?', dest='input_path',
                                help='The CSV file to operate on. If omitted, will accept input as piped data via STDIN.')

    cparser.add_argument('-d', '--delimiter', dest='delimiter',
                                help='Delimiting character of the input CSV file.')
    cparser.add_argument('-t', '--tabs', dest='tabs', action='store_true',
                                help='Specify that the input CSV file is delimited with tabs. Overrides "-d".')
    cparser.add_argument('-q', '--quotechar', dest='quotechar',
                                help='Character used to quote strings in the input CSV file.')

    cparser.add_argument('-u', '--quoting', dest='quoting', type=int, choices=[0, 1, 2, 3],
                                help='Quoting style used in the input CSV file. 0 = Quote Minimal, 1 = Quote All, 2 = Quote Non-numeric, 3 = Quote None.')

    cparser.add_argument('-b', '--no-doublequote', dest='doublequote', action='store_false',
                                help='Whether or not double quotes are doubled in the input CSV file.')

    cparser.add_argument('-p', '--escapechar', dest='escapechar',
                                help='Character used to escape the delimiter if --quoting 3 ("Quote None") is specified and to escape the QUOTECHAR if --no-doublequote is specified.')

    cparser.add_argument('-z', '--maxfieldsize', dest='field_size_limit', type=int,
                                help='Maximum length of a single field in the input CSV file.')

    cparser.add_argument('-e', '--encoding', dest='encoding', default='utf-8',
                                help='Specify the encoding of the input CSV file.')
    cparser.add_argument('-S', '--skipinitialspace', dest='skipinitialspace', action='store_true',
                                help='Ignore whitespace immediately following the delimiter.')

    cparser.add_argument('--blanks', dest='blanks', action='store_true',
                                help='Do not convert "", "na", "n/a", "none", "null", "." to NULL.')

    cparser.add_argument('-H', '--no-header-row', dest='no_header_row', action='store_true',
                                help='Specify that the input CSV file has no header row. Will create default headers (a,b,c,...).')
    cparser.add_argument('-K', '--skip-lines', dest='skip_lines', type=int, default=0,
                                help='Specify the number of initial lines to skip before the header row (e.g. comments, copyright notices, empty rows).')
    cparser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                                help='Print detailed tracebacks when errors occur.')
    cparser.add_argument('--zero', dest='zero_based', action='store_true',
                                help='When interpreting or displaying column numbers, use zero-based numbering instead of the default 1-based numbering.')


    cparser.add_argument('-y', '--snifflimit', dest='sniff_limit', type=int,
                            help='Limit CSV dialect sniffing to the specified number of bytes. Specify "0" to disable sniffing entirely.')
    cparser.add_argument('-I', '--no-inference', dest='no_inference', action='store_true',
                            help='Disable type inference when parsing the input.')




class CSVChart(AgatableUtil):
    description = """Simple charting"""


    def _init_common_parser(self):
        self.argparser = argparse.ArgumentParser(description=self.description, epilog=self.epilog)

        # Input
        # if 'f' not in self.override_flags:

        self.argparser.add_argument('-V', '--version', action='version', version='%(prog)s 1.0.5',
                                    help='Display version information and exit.')

    def add_arguments(self):

        subparsers = self.argparser.add_subparsers(title='chart',
                dest='chart_type', metavar='CHART_TYPE',
                help='Specify a chart type, e.g. bar, line, pie')

        self.bar_parser = subparsers.add_parser('bar', help='Make a bar chart')
        self.bar_parser.add_argument('-X', '--xvar', dest='xvar', type=str, help='The column to use as labels')
        self.bar_parser.add_argument('-Y', '--yvar', dest='yvar', type=str, help='The column to use as values')
        self.bar_parser.add_argument('-C', '--colorvar', dest='colorvar', type=str, help='Optional: a column to do series/stacking')

        self.column_parser = subparsers.add_parser('column', help='Make a column chart')
        self.column_parser.add_argument('-X', '--xvar', dest='xvar', type=str, help='The column to use as labels')
        self.column_parser.add_argument('-Y', '--yvar', dest='yvar', type=str, help='The column to use as values')
        self.column_parser.add_argument('-C', '--colorvar', dest='colorvar', type=str, help='Optional: a column to do series/stacking')


        custom_init_common_parser(self.bar_parser)
        custom_init_common_parser(self.column_parser)


    def main(self):

        if self.additional_input_expected():
            self.argparser.error('You must provide an input file or piped data.')


        agtable = agate.Table.from_csv(
            self.input_file,
            skip_lines=self.args.skip_lines,
            sniff_limit=self.args.sniff_limit,
            **self.reader_kwargs
        )
        column_names = agtable.column_names

        df = agate_to_df(agtable)


        if self.args.chart_type in ('column', 'bar'):
            # _xid = parse_column_identifiers(
            #     self.args.xvar,
            #     column_names,
            #     column_offset=1,  # TK, do I need to worry about this?
            #     excluded_columns=getattr(self.args, 'not_columns', None)
            # )

            # _yid = parse_column_identifiers(
            #     self.args.yvar,
            #     column_names,
            #     column_offset=1,  # TK, do I need to worry about this?
            #     excluded_columns=getattr(self.args, 'not_columns', None)
            # )

            # if (len(_xid)) != 1:
            #     raise ArgumentErrorTK(f'--xvar must point to a single column id/name, not {_xid=}')
            # elif (len(_yid)) != 1:
            #     raise ArgumentErrorTK(f'--yvar must point to a single column id/name, not {_yid=}')


            # xcol = column_names[_xid[0]]
            # ycol = column_names[_yid[0]]

            xvar = self.args.xvar if self.args.xvar else column_names[0]
            yvar = self.args.yvar if self.args.yvar else column_names[1]
            colorvar = self.args.colorvar

            if self.args.chart_type == 'bar':
                # altair horizontal charts switch up how x and y are encoded
                # https://altair-viz.github.io/gallery/bar_chart_horizontal.html
                chartargs = {'y': xvar, 'x': yvar }
            elif self.args.chart_type == 'column':
                chartargs = {'x': xvar, 'y': yvar }


        if colorvar:
            chartargs['color'] = colorvar

        chartargs['tooltip'] = [xvar, yvar]

        chart = alt.Chart(df).mark_bar().encode(**chartargs)
        altview.show(chart.interactive())


def launch_new_instance():
    utility = CSVChart()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()

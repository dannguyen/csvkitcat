#!/usr/bin/env python


from sys import argv, stderr, stdin
from os import isatty

import six
import warnings

from typing import Iterable as typeIterable, NoReturn as typeNoReturn, List as typeList


from csvkit.grep import FilteringCSVReader
from csvkit.utilities.csvgrep import CSVGrep


from csvkitcat import agate, parse_column_identifiers, rxlib as re
from csvkitcat.kitcat.justtext import JustTextUtility



class CSVRgrep(JustTextUtility):
    description = "Like csvgrep, except with support for multiple expressions"
    override_flags = ["f", "L", "blanks", "date-format", "datetime-format"]

    def add_arguments(self):
        def option_parser_flag(bytestring=None):
            if bytestring is None:
                return True
            elif six.PY2:
                return bytestring.decode(sys.getfilesystemencoding())
            else:
                return bytestring

        self.argparser.add_argument(
            "-E",
            "--expr",
            dest="expressions_list",
            action="append",
            nargs="*",
            help="Store a list of patterns to match",
        )


        self.argparser.add_argument(
            "-m",
            "--literal-match",
            dest="literal_match",
            action="store_true",
            # type=option_parser_flag,
            default=False,
            # nargs='?',
            help="Match patterns literally instead of using regular expressions",
        )

        self.argparser.add_argument(
            "-n",
            "--names",
            dest="names_only",
            action="store_true",
            help="Display column names and indices from the input CSV and exit.",
        )
        self.argparser.add_argument(
            "-c",
            "--columns",
            dest="columns",
            help='A comma separated list of column indices, names or ranges to be searched, e.g. "1,id,3-5".',
        )

        self.argparser.add_argument(
            "-i",
            "--invert-match",
            dest="inverse",
            action="store_true",
            help="If specified, select non-matching instead of matching rows.",
        )
        self.argparser.add_argument(
            "-a",
            "--all-match",
            dest="all_match",
            action="store_true",
            help="If specified, only select rows for which every column matches the given pattern",
        )


        self.argparser.add_argument(metavar='PATTERN', dest='first_pattern', type=str,
                                    # nargs='?',
                                    help='A pattern to search for',)


        self.argparser.add_argument(
            metavar="FILE",
            nargs="?",
            dest="input_path",
            help="The CSV file to operate on. If omitted, will accept input as piped data via STDIN.",
        )

    def run(self):
        """
        A wrapper around the main loop of the utility which handles opening and
        closing files.
        """

        # TODO: SPAGHETTI HACK; untangle later
        if self.args.names_only:
            if not self.args.first_pattern and not self.args.input_path:
                # attempt stdin
                # print('opening None')
                self.input_file = self._open_input_file(None)
            elif self.args.first_pattern and not self.args.input_path:
                if not isatty(stdin.fileno()):
                    # then stdin has data
                    # print(f'have pattern, but opening stdin')
                    self.input_file = self._open_input_file(None)
                else:
                    # assume that first_pattern ate up the input_path
                    # print(f'opening first_pattern: {self.args.first_pattern}')
                    self.input_file = self._open_input_file(self.args.first_pattern)
            else:
                # print(f'opening input_path: {self.args.input_path}')
                self.input_file = self._open_input_file(self.args.input_path)
            self.print_column_names()
            self.input_file.close()
            return


        self.last_expr = []
        if not self.args.input_path:
            # then it must have been eaten by an -E flag; we assume the input file is in last_expr[-1],
            # where `last_expr` is the last member of expressions_list

            if self.args.expressions_list:
                self.last_expr = self.args.expressions_list[-1]

                if len(self.last_expr) > 1:
                    # could be either 2 or 3
                    self.args.input_path = self.last_expr.pop()
                elif len(self.last_expr) == 1:
                    pass
                    # do nothing, but be warned that if there is no stdin,
                    # then -E might have eaten up the input_file argument
                    # and interpreted it as pattern
                else:
                    # else, last_expr has an implied second argument, and
                    # input_path is hopefully stdin
                    self.args.input_path = None

        self.input_file = self._open_input_file(self.args.input_path)

        try:
            with warnings.catch_warnings():
                if getattr(self.args, "no_header_row", None):
                    warnings.filterwarnings(
                        action="ignore",
                        message="Column names not specified",
                        module="agate",
                    )

                self.main()
        finally:
            self.input_file.close()

    def _handle_expressions(self) -> typeList:
        expressions = []
        first_pattern = self.args.first_pattern
        first_colstring = self.args.columns if self.args.columns else ''
        expressions.append([first_pattern, first_colstring])

        # if not exlist:
        #     self.argparser.error("Must specify at least one -E/--expr expression")

        if exlist := getattr(self.args, 'expressions_list'):
            for i, _e in enumerate(exlist):
                ex = _e.copy()
                if len(ex) < 1 or len(ex) > 2:
                    self.argparser.error(
                        f"""-E/--expr takes 1 or 2 arguments, not {len(ex)}: {ex}"""
                    )

                if len(ex) == 1:
                    # blank column_str argument is interpreted as "use -c/--columns value"
                    ex.append(first_colstring)

                expressions.append(ex)

        return expressions

    def main(self):

        if self.additional_input_expected():
            if len(self.last_expr) == 1:
                stderr.write(
                    f"""WARNING: the last positional argument – {self.last_expr[0]} – is interpreted as the first and only argument to -E/--expr, i.e. the pattern to search for.\n"""
                )
                stderr.write("Make sure that it isn't meant to be the name of your input file!\n\n")
            stderr.write(
                "No input file or piped data provided. Waiting for standard input:\n"
            )


        self.expressions = self._handle_expressions()

        _all_match = self.args.all_match
        _any_match = not _all_match
        _inverse = self.args.inverse
        _literal_match = self.args.literal_match
        _column_offset = self.get_column_offset()


        myio = self.init_io(write_header=True)
        xrows = myio.rows


        for epattern, ecolstring in self.expressions:
            xrows = filter_rows(
                xrows,
                epattern,
                ecolstring,
                myio.column_names,
                myio.column_ids,
                literal_match=_literal_match,
                column_offset=_column_offset,
                inverse=_inverse,
                any_match=_any_match,
                # not_columns=_not_columns,
            )


        for row in xrows:
            myio.output.writerow(row)


def launch_new_instance():
    utility = CSVRgrep()
    utility.run()


def filter_rows(
    rows: typeIterable,
    pattern_str: str,
    columns_str: str,
    column_names: list,
    default_column_ids: list,
    literal_match: bool,
    column_offset: int,
    inverse: bool,
    any_match: bool,
    # not_columns,
) -> FilteringCSVReader:

    if literal_match:
        pattern = pattern_str
    else:  # literal match
        pattern = re.compile(pattern_str)

    if columns_str:
        expr_col_ids = parse_column_identifiers(
            columns_str, column_names, column_offset,
        )
    else:
        expr_col_ids = default_column_ids

    epatterns = dict((eid, pattern) for eid in expr_col_ids)

    filtered_rows = FilteringCSVReader(
        rows,
        header=False,
        patterns=epatterns,
        inverse=inverse,
        any_match=any_match,
    )
    return filtered_rows




if __name__ == "__main__":
    launch_new_instance()

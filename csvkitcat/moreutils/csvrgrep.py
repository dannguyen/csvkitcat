#!/usr/bin/env python


from sys import argv, stderr
import six
import warnings

from typing import Iterable as typeIterable

from csvkit.grep import FilteringCSVReader

from csvkit.utilities.csvgrep import CSVGrep
from csvkitcat import agate, parse_column_identifiers, rxlib as re






class CSVRgrep(CSVGrep):
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

        if not self.args.input_path:
            # then it must have been eaten by an -E flag; we assume the input file is in last_expr[-1],
            # where `last_expr` is the last member of expressions_list
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

    def main(self):
        if self.args.names_only:
            self.print_column_names()
            return

        if self.additional_input_expected():
            if len(self.last_expr) == 1:
                stderr.write(
                    f"""WARNING: the last positional argument – {self.last_expr[0]} – is interpreted as the first and only argument to -E/--expr, i.e. the pattern to search for.\n"""
                )
                stderr.write("Make sure that it isn't meant to be the name of your input file!\n\n")
            stderr.write(
                "No input file or piped data provided. Waiting for standard input:\n"
            )

        if not self.args.expressions_list:
            self.argparser.error("Must specify at least one -E/--expr expression")

        for i, e in enumerate(self.args.expressions_list):
            if len(e) == 0:
                self.argparser.error(
                    "-E/--expr requires at least 1 argument, a pattern to be grepped"
                )
            if len(e) > 2:
                self.argparser.error(
                    f"""-E/--expr takes 1 or 2 arguments, not {len(e)}: {e}"""
                )

            if len(e) < 2:
                # blank column_str argument is interpreted as "use -c/--columns value"
                e.append("")


        self.all_match = self.args.all_match
        self.any_match = not self.all_match
        self.literal_match = self.args.literal_match
        self.column_offset = self.get_column_offset()
        self.not_columns = getattr(self.args, "not_columns", None)

        reader_kwargs = self.reader_kwargs
        writer_kwargs = self.writer_kwargs
        # Move the line_numbers option from the writer to the reader.
        if writer_kwargs.pop("line_numbers", False):
            reader_kwargs["line_numbers"] = True

        (
            rows,
            column_names,
            default_column_ids,
        ) = self.get_rows_and_column_names_and_column_ids(**reader_kwargs)


        for epattern, ecolstring in self.args.expressions_list:
            rows = filter_rows(
                rows,
                epattern,
                ecolstring,
                column_names,
                default_column_ids,
                literal_match=self.literal_match,
                column_offset=self.column_offset,
                inverse=self.args.inverse,
                any_match=self.any_match,
                not_columns=self.not_columns,
            )

        output = agate.csv.writer(self.output_file, **writer_kwargs)
        output.writerow(column_names)

        for row in rows:
            output.writerow(row)


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
    not_columns,
) -> FilteringCSVReader:

    if literal_match:
        pattern = pattern_str
    else:  # literal match
        pattern = re.compile(pattern_str)

    if columns_str:
        expr_col_ids = parse_column_identifiers(
            columns_str, column_names, column_offset, not_columns
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

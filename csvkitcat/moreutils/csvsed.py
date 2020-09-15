#!/usr/bin/env python

from csvkitcat.kitcat.justtext import JustTextUtility
from csvkitcat.moreutils.csvrgrep import CSVRgrep, filter_rows
from csvkitcat import agate, rxlib as re
from csvkitcat import parse_column_identifiers
import warnings

from sys import stderr
from typing import List as typeList


class CSVSed(JustTextUtility):
    description = """Replaces all instances of [PATTERN] with [REPL]"""

    override_flags = ["f", "L", "blanks", "date-format", "datetime-format"]

    def add_arguments(self):
        self.argparser.add_argument(
            "-c",
            "--columns",
            dest="columns",
            help='A comma separated list of column indices, names or ranges to be searched, e.g. "1,id,3-5".',
        )

        self.argparser.add_argument(
            "-E",
            "--expr",
            dest="expressions_list",
            # required=True,
            nargs="*",
            action="append",
            type=str,
            help=r"""
                                        When you want to do multiple sed_expressions:
                                            -E 'PATTERN' 'REPL' '[names_of_columns]'

                                            'names_of_columns' is a comma-delimited list of columns; it cannot refer to
                                                columns *not included* in the `-c/--columns` flag; leave blank to match all columns

                                        e.g.
                                        -E '(?i)\b(bob|bobby|rob)\b' 'Robert' 'first_name' \
                                        -E '^(?i)smith$' 'SMITH' 'last_name' \
                                        -E '(\d{2})-(\d{3})' '$1:$2' '' \
                                        """,
        )

        self.argparser.add_argument(
            "-m",
            "--match-literal",
            dest="literal_match",
            action="store_true",
            default=False,
            help="By default, [PATTERN] is assumed to be a regex. Set this flag to make it a literal text find/replace",
        )

        self.argparser.add_argument(
            "-G",
            "--like-grep",
            dest="like_grep",
            action="store_true",
            default=False,
            help="""Only return rows in which [PATTERN] was a match (BEFORE any transformations) – i.e. like grep''s traditional behavior""",
        )

        self.argparser.add_argument(
            "-R",
            "--replace",
            dest="replace_value",
            action="store_true",
            default=False,
            help="Replace entire field with [REPL], instead of just the substring matched by [PATTERN]",
        )

        self.argparser.add_argument(
            "--max",
            dest="max_match_count",
            action="store",
            default=0,
            type=int,
            help="Max number of matches to replace PER FIELD. Default is 0, i.e. no limit",
        )

        self.argparser.add_argument(
            metavar="PATTERN",
            dest="first_pattern",
            type=str,
            # nargs='?',
            help="A pattern to search for",
        )

        self.argparser.add_argument(
            metavar="REPL",
            dest="first_repl",
            type=str,
            # nargs='?',
            help="A replacement pattern",
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

        TK: This is copy-pasted form CSVKitUtil because we have to override 'f'; maybe there's
            a way to refactor this...

        csvsed has special functionality, in which the presence of `-E/--expr` changes the command signature,
            i.e. from: csvsed PATTERN REPL input.csv
                 to: csvsed -E 'PATTERN' 'REPL' 'COLUMNS' -E x y z input.csv
        """

        self.last_expr = []
        if not self.args.input_path:
            # then it must have been eaten by an -E flag; we assume the input file is in last_expr[-1],
            # where `last_expr` is the last member of expressions_list

            # TODO: THIS IS CRAP
            if self.args.expressions_list:
                self.last_expr = self.args.expressions_list[-1]

                if len(self.last_expr) > 2:
                    # could be either 3 or 4
                    self.args.input_path = self.last_expr.pop()
                elif len(self.last_expr) == 2:
                    pass
                    # do nothing, but be warned that if there is no stdin,
                    # then -E might have eaten up the input_file argument
                    # and interpreted it as pattern
                else:
                    # else, last_expr has an implied third argument, and
                    # input_path is hopefully stdin
                    self.args.input_path = None

            # # # error handling
            # #  if self.args.pattern or self.args.repl:
            # #      self.argparser.error("If using -E/--expr, [PATTERN] and [REPL] arguments cannot be filled in")

            # #  if not self.args.input_path and self.args.pattern and not self.args.repl:
            # #      self.args.input_path = self.args.pattern
            # #      delattr(self.args, 'pattern')
            # #      delattr(self.args, 'repl')
            # #  elif self.args.input_path and self.args.pattern:
            # #      # if input_path was given AND self.args.pattern (i.e. any other positional args besides INPUT_PATH)
            # #      self.argparser.error(f"""Got an unexpected positional argument; either:
            # #          - More than 3 arguments for -E/--expr {exes[-1]}
            # #          - Or, a PATTERN argument, which is invalid when using -E/--expr
            # #      """)
            # #  else:
            # #      self.argparser.error("Some other unhandled positional arg thingy [TODO]")
            # q

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

    def _handle_sed_expressions(self) -> typeList:
        # TODO: fix this spaghetti CRAP: maybe make expressions handle dicts/named typles instead of lists

        first_col_str = self.args.columns if self.args.columns else ""
        first_expr = [self.args.first_pattern, self.args.first_repl, first_col_str]
        expressions = [first_expr]
        if list_expressions := getattr(self.args, "expressions_list", []):
            for i, _e in enumerate(list_expressions):
                ex = _e.copy()

                if len(ex) < 2 or len(ex) > 3:
                    self.argparser.error(
                        f"-E/--expr takes 2 or 3 arguments; you provided {len(ex)}: {ex}"
                    )

                if len(ex) == 2:
                    ex.append(first_col_str)

                expressions.append(ex)

        for ex in expressions:
            # this branch re-loops through the_expressions and fixes any leading dashes in the repls
            if ex[1][0:2] == r"\-":
                ex[1] = ex[1][1:]

            # compile the pattern into a regex
            if not self.literal_match_mode:
                ex[0] = re.compile(ex[0])

            # set the column_ids
            ex[2] = parse_column_identifiers(
                ex[2], self.all_column_names, self.column_offset, None
            )

        return expressions

    def main(self):
        # TODO: THIS IS CRAP
        if self.additional_input_expected():
            if len(self.last_expr) == 2:
                stderr.write(
                    f"""WARNING: the last positional argument – {self.last_expr[0]} – is interpreted as the first and only argument to -E/--expr, i.e. the pattern to search for.\n"""
                )
                stderr.write(
                    "Make sure that it isn't meant to be the name of your input file!\n\n"
                )
            stderr.write(
                "No input file or piped data provided. Waiting for standard input:\n"
            )

        self.literal_match_mode = self.args.literal_match
        self.replace_value_mode = self.args.replace_value

        self.max_match_count = self.args.max_match_count
        if (
            self.max_match_count < 1
        ):  # because str.replace and re.sub use a different catchall/default value
            self.max_match_count = -1 if self.literal_match_mode else 0

        myio = self.init_io(write_header=True)
        self.all_column_names = myio.column_names
        self.all_column_ids = myio.column_ids
        self.column_offset = self.get_column_offset()

        self.expressions = self._handle_sed_expressions()

        xrows = myio.rows
        # here's where we emulate csvrgrep...
        if self.args.like_grep:

            epattern = self.args.first_pattern
            ecolstring = self.args.columns

            xrows = filter_rows(
                xrows,
                epattern,
                ecolstring,
                self.all_column_names,
                self.all_column_ids,
                literal_match=self.literal_match_mode,
                column_offset=self.column_offset,
                inverse=False,
                any_match=True,
            )

        # TODO: fix spaghetti
        # for each row, and for each column value
        #  we iterate through each expression
        #     and attempt/apply the substitution on the given column value,
        #     i.e. newval
        for row in xrows:
            new_row = []

            for cid, val in enumerate(row):
                newval = val

                for ex in self.expressions:
                    pattern, repl, col_ids = ex
                    if cid in col_ids:
                        repl = fr"{repl}"

                        if not self.replace_value_mode:
                            newval = (
                                pattern.sub(repl, newval, self.max_match_count)
                                if not self.literal_match_mode
                                else newval.replace(pattern, repl, self.max_match_count)
                            )

                        elif self.replace_value_mode:
                            if not self.literal_match_mode:
                                mx = pattern.search(newval)
                                newval = (
                                    pattern.sub(repl, mx.group(0)) if mx else newval
                                )
                            elif self.literal_match_mode:
                                newval = repl if pattern in newval else newval
                            else:
                                pass  # there is no else; I just want to explicitly mention self.literal_match_mode
                        else:
                            pass  # there is no else; I just want to explicitly mention self.replace_value_mode

                new_row.append(newval)
                # end of expression-iteration; move on to the next column val

            myio.output.writerow(new_row)
            # end of column-value iteration, move on to the next row


def launch_new_instance():
    utility = CSVSed()
    utility.run()


if __name__ == "__main__":
    launch_new_instance()

#!/usr/bin/env python

from csvkitcat.kitcat.justtext import JustTextUtility
from csvkitcat.moreutils.csvrgrep import CSVRgrep, filter_rows
from csvkitcat import rxlib as re
from csvkitcat import parse_column_identifiers

import agate
import warnings

from sys import stderr
from typing import List as typeList


class CSVSed(JustTextUtility):
    description = """Replaces all instances of [PATTERN] with [REPL]"""

    override_flags = ['f', 'L', 'blanks', 'date-format', 'datetime-format']


    def add_arguments(self):
        self.argparser.add_argument('-c', '--columns', dest='columns',
                                    help='A comma separated list of column indices, names or ranges to be searched, e.g. "1,id,3-5".')

        self.argparser.add_argument('-E', '--expr', dest='expressions_list',
                                        required=True,
                                        nargs='*',
                                        action='append',
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


        self.argparser.add_argument('-m', '--match-literal', dest="literal_match", action='store_true',
                                    default=False,
                                    help='By default, [PATTERN] is assumed to be a regex. Set this flag to make it a literal text find/replace',)


        self.argparser.add_argument('-G', '--like-grep', dest='like_grep', action='store_true',
                                    default=False,
                                    help="""Only return rows in which [PATTERN] was a match (BEFORE any transformations) – i.e. like grep''s traditional behavior""")


        self.argparser.add_argument('-R', '--replace', dest="replace_value", action='store_true',
                                    default=False,
                                    help='Replace entire field with [REPL], instead of just the substring matched by [PATTERN]',)


        self.argparser.add_argument('--max', dest="max_match_count", action='store',
                                    default=0,
                                    type=int,
                                    help='Max number of matches to replace PER FIELD. Default is 0, i.e. no limit')


        self.argparser.add_argument(metavar='FILE', nargs='?', dest='input_path',
                                    help='The CSV file to operate on. If omitted, will accept input as piped data via STDIN.')





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


        if not self.args.input_path:
            # then it must have been eaten by an -E flag; we assume the input file is in last_expr[-1],
            # where `last_expr` is the last member of expressions_list
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
                if getattr(self.args, 'no_header_row', None):
                    warnings.filterwarnings(action='ignore', message='Column names not specified', module='agate')

                self.main()
        finally:
            self.input_file.close()



    def _handle_sed_expressions(self) -> typeList:
        # 'E/--expr' is required
        expressions_list = getattr(self.args, 'expressions_list')
        # expressions_list = expressions_list.copy() if expressions_list else []

        # self.sed_expressions = getattr(self.args, 'expressions_list', [])

        # if not expressions_list:
        #     # then PATTERN and REPL are set positionally
        #     if not (self.args.pattern and self.args.repl):
        #         self.parser.error("Both [PATTERN] and [REPL] arguments need to be filled when not using -E/--expr")

        #     exp = [self.args.pattern, self.args.repl, ''] # 3rd argument is the sub-columns to filter by, but can be empty by default
        #     self.sed_expressions =[exp,]
        # else:

            # def _build_sedexprlist():
        the_expressions = []

        for i, _e in enumerate(expressions_list):
            ex = _e.copy()

            if len(ex) < 2 or len(ex) > 3:
                self.argparser.error(
                    f"-E/--expr takes 2 or 3 arguments; you provided {len(ex)}: {ex}"
                )

            if len(ex) == 2:
                # blank column_str argument is interpreted as "use -c/--columns value"
                ex.append('')

            the_expressions.append(ex)

        return the_expressions


    def main(self):
        if self.additional_input_expected():
            if len(self.last_expr) == 2:
                stderr.write(
                    f"""WARNING: the last positional argument – {self.last_expr[0]} – is interpreted as the first and only argument to -E/--expr, i.e. the pattern to search for.\n"""
                )
                stderr.write("Make sure that it isn't meant to be the name of your input file!\n\n")
            stderr.write(
                "No input file or piped data provided. Waiting for standard input:\n"
            )


        self.expressions = self._handle_sed_expressions()


        reader_kwargs = self.reader_kwargs
        writer_kwargs = self.writer_kwargs

        max_match_count = self.args.max_match_count
        if max_match_count < 1: # because str.replace and re.sub use a different catchall/default value
            max_match_count = -1 if self.args.literal_match else 0


        rows, all_column_names, selected_column_ids = self.get_rows_and_column_names_and_column_ids(**reader_kwargs)


        # here's where we emulate csvrgrep...
        if self.args.like_grep:
            self.not_columns = getattr(self.args, "not_columns", None),
            self.column_offset = self.get_column_offset()

            for e in self.expressions:
                epattern = e[0]
                ecolstring = e[2] # if e[2] else selected_column_ids

                rows = filter_rows(
                    rows,
                    epattern,
                    ecolstring,
                    all_column_names,
                    selected_column_ids,
                    literal_match=self.args.literal_match,
                    column_offset=self.column_offset,
                    inverse=False,
                    any_match=True,
                )


        all_patterns = []
        for e in self.expressions:
            pattern, repl, ecol_string = e
            if not self.args.literal_match:
                e[0] = pattern = re.compile(pattern)

            if ecol_string:
                 # TODO: this should throw an error of ecol_str refers to columns not in all_column_ids
                ecol_ids = parse_column_identifiers(ecol_string, all_column_names, self.get_column_offset(), getattr(self.args, 'not_columns', None))
            else:
                ecol_ids = selected_column_ids
            e[2] =  ecol_ids

            ecol_names = [all_column_names[i] for i in ecol_ids]
            all_patterns.append([ecol_names, pattern])



        output = agate.csv.writer(self.output_file, **writer_kwargs)
        output.writerow(all_column_names)


        for row in rows:
            d = []
            for v_id, val in enumerate(row):
                newval = val

                for ex in self.expressions:
                    pattern, repl, _xids = ex
                    excol_ids = _xids if _xids else selected_column_ids  # todos: this should be handled earlier

                    if v_id in excol_ids:
                        if self.args.replace_value:
                            if self.args.literal_match:
                                newval = repl if pattern in newval else newval
                            else:
                                mx = pattern.search(newval)
                                if mx:
                                    newval = pattern.sub(repl, mx.group(0))
                        else:
                            if self.args.literal_match:
                                newval = newval.replace(pattern, repl, max_match_count)
                            else:
                                newval = pattern.sub(repl, newval, max_match_count)
                d.append(newval)

            output.writerow(d)


def launch_new_instance():
    utility = CSVSed()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()

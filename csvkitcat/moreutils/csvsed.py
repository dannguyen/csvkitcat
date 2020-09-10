#!/usr/bin/env python

from csvkitcat.alltext import AllTextUtility
from csvkitcat.moreutils.csvrgrep import CSVRgrep, filter_rows
from csvkitcat import rxlib as re
from csvkitcat import parse_column_identifiers

import agate
import warnings

from sys import stderr
from typing import NoReturn as typeNoReturn


class CSVSed(AllTextUtility):
    description = """Replaces all instances of [PATTERN] with [REPL]"""

    override_flags = ['f', 'L', 'blanks', 'date-format', 'datetime-format']


    def add_arguments(self):
        self.argparser.add_argument('-c', '--columns', dest='columns',
                                    help='A comma separated list of column indices, names or ranges to be searched, e.g. "1,id,3-5".')
        self.argparser.add_argument('-m', '--match', dest="literal_match", action='store_true',
                                    default=False,
                                    help='By default, [PATTERN] is assumed to be a regex. Set this flag to make it a literal text find/replace',)


        self.argparser.add_argument('--max', dest="max_match_count", action='store',
                                    default=0,
                                    type=int,
                                    help='Max number of matches to replace PER FIELD. Default is 0, i.e. no limit')



        self.argparser.add_argument('-R', '--replace', dest="replace_value", action='store_true',
                                    default=False,
                                    help='Replace entire field with [REPL], instead of just the substring matched by [PATTERN]',)

        self.argparser.add_argument('-G', '--like-grep', dest='like_grep', action='store_true',
                                    default=False,
                                    help="""Only return rows in which [PATTERN] was matched, i.e. like grep''s traditional behavior""")


        self.argparser.add_argument('-E', '--expr', dest='expressions_list',
                                        nargs=3,
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

        self.argparser.add_argument(metavar='PATTERN', dest='pattern',
                                    nargs='?',
                                    help='A regex pattern to find')

        self.argparser.add_argument(metavar='REPL', dest='repl',
                                    nargs='?',
                                    help='A regex pattern to replace with')


        self.argparser.add_argument(metavar='FILE', nargs='?', dest='input_path',
                                    help='The CSV file to operate on. If omitted, will accept input as piped data via STDIN.')

    #     ###########boilerplate
        self.argparser.add_argument('-D', '--out-delimiter', dest='out_delimiter',
                                    help='Delimiting character of the output CSV file.')
        self.argparser.add_argument('-T', '--out-tabs', dest='out_tabs', action='store_true',
                                    help='Specify that the output CSV file is delimited with tabs. Overrides "-D".')
        self.argparser.add_argument('-Q', '--out-quotechar', dest='out_quotechar',
                                    help='Character used to quote strings in the output CSV file.')
        self.argparser.add_argument('-U', '--out-quoting', dest='out_quoting', type=int, choices=[0, 1, 2, 3],
                                    help='Quoting style used in the output CSV file. 0 = Quote Minimal, 1 = Quote All, 2 = Quote Non-numeric, 3 = Quote None.')
        self.argparser.add_argument('-B', '--out-no-doublequote', dest='out_doublequote', action='store_false',
                                    help='Whether or not double quotes are doubled in the output CSV file.')
        self.argparser.add_argument('-P', '--out-escapechar', dest='out_escapechar',
                                    help='Character used to escape the delimiter in the output CSV file if --quoting 3 ("Quote None") is specified and to escape the QUOTECHAR if --no-doublequote is specified.')
        self.argparser.add_argument('-M', '--out-lineterminator', dest='out_lineterminator',
                                    help='Character used to terminate lines in the output CSV file.')


    def _extract_csv_writer_kwargs(self):
        kwargs = {}

        # if self.args.line_numbers:
        #     kwargs['line_numbers'] = True

        if self.args.out_tabs:
            kwargs['delimiter'] = '\t'
        elif self.args.out_delimiter:
            kwargs['delimiter'] = self.args.out_delimiter


        for arg in ('quotechar', 'quoting', 'doublequote', 'escapechar', 'lineterminator'):
            value = getattr(self.args, 'out_%s' % arg)
            if value is not None:
                kwargs[arg] = value

        return kwargs




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

        def _handle_sed_expressions() -> typeNoReturn:
            self.sed_expressions = getattr(self.args, 'expressions_list', [])

            if not self.sed_expressions:
                # then PATTERN and REPL are set positionally
                exp = [self.args.pattern, self.args.repl, ''] # 3rd argument is the sub-columns to filter by, but can be empty by default
                self.sed_expressions =[exp,]
            else:
                # error handling
                if not self.args.input_path and self.args.pattern and not self.args.repl:
                    self.args.input_path = self.args.pattern
                    delattr(self.args, 'pattern')
                    delattr(self.args, 'repl')
                elif self.args.input_path and self.args.pattern:
                    # if input_path was given AND self.args.pattern (i.e. any other positional args besides INPUT_PATH)
                    self.parser.error(f"""Got an unexpected positional argument; either:
                        - More than 3 arguments for -E/--expr {exes[-1]}
                        - Or, a PATTERN argument, which is invalid when using -E/--expr
                    """)
                else:
                    self.parser.error("Some other unhandled positional arg thingy [TODO]")


        _handle_sed_expressions()
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

        reader_kwargs = self.reader_kwargs
        writer_kwargs = self.writer_kwargs

        max_match_count = self.args.max_match_count
        if max_match_count < 1: # because str.replace and re.sub use a different catchall/default value
            max_match_count = -1 if self.args.literal_match else 0


        rows, all_column_names, selected_column_ids = self.get_rows_and_column_names_and_column_ids(**reader_kwargs)


        if self.args.like_grep:
            self.not_columns = getattr(self.args, "not_columns", None),
            self.column_offset = self.get_column_offset()

            for e in self.sed_expressions:
                epattern = e[0]
                ecolstring = e[2] if len(e) == 3 else ''

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
                    not_columns=self.not_columns
                )




        all_patterns = []
        for e in self.sed_expressions:
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

                for ex in self.sed_expressions:
                    pattern, repl, _xids = ex
                    excol_ids = _xids if _xids else selected_column_ids  # todos: this should be handled earlier

                    if v_id in excol_ids:
                        if self.args.replace_value:
                            if self.args.literal_match:
                                newval = repl if pattern in val else val
                            else:
                                mx = pattern.search(val)
                                if mx:
                                    newval = pattern.sub(repl, mx.group(0))
                        else:
                            if self.args.literal_match:
                                newval = val.replace(pattern, repl, max_match_count)
                            else:
                                newval = pattern.sub(repl, val, max_match_count)
                d.append(newval)

            output.writerow(d)


def launch_new_instance():
    utility = CSVSed()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()

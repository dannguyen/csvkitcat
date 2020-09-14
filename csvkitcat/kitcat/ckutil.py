from csvkitcat import CSVKitUtility,  __title__, __version__
import argparse


class CSVKitcatUtil(CSVKitUtility):
    """
    slightly adjusted version of standard CSVKitUtility
    """


    def get_column_offset(self):
        """a dumb hack I need for some reason? Because sometimes I need to call this when zero_based is not an arg"""
        if getattr(self.args, 'zero_based', None):
            if self.args.zero_based:
                return 0
            else:
                return 1
        else:
            return 1



    def _init_common_parser(self):
        """
        Same as csvkit.cli.CSVKitUtil 1.05, except --version is customized
        """
        self.argparser = argparse.ArgumentParser(description=self.description, epilog=self.epilog)

        # Input
        if 'f' not in self.override_flags:
            self.argparser.add_argument(metavar='FILE', nargs='?', dest='input_path',
                                        help='The CSV file to operate on. If omitted, will accept input as piped data via STDIN.')
        if 'd' not in self.override_flags:
            self.argparser.add_argument('-d', '--delimiter', dest='delimiter',
                                        help='Delimiting character of the input CSV file.')
        if 't' not in self.override_flags:
            self.argparser.add_argument('-t', '--tabs', dest='tabs', action='store_true',
                                        help='Specify that the input CSV file is delimited with tabs. Overrides "-d".')
        if 'q' not in self.override_flags:
            self.argparser.add_argument('-q', '--quotechar', dest='quotechar',
                                        help='Character used to quote strings in the input CSV file.')
        if 'u' not in self.override_flags:
            self.argparser.add_argument('-u', '--quoting', dest='quoting', type=int, choices=[0, 1, 2, 3],
                                        help='Quoting style used in the input CSV file. 0 = Quote Minimal, 1 = Quote All, 2 = Quote Non-numeric, 3 = Quote None.')
        if 'b' not in self.override_flags:
            self.argparser.add_argument('-b', '--no-doublequote', dest='doublequote', action='store_false',
                                        help='Whether or not double quotes are doubled in the input CSV file.')
        if 'p' not in self.override_flags:
            self.argparser.add_argument('-p', '--escapechar', dest='escapechar',
                                        help='Character used to escape the delimiter if --quoting 3 ("Quote None") is specified and to escape the QUOTECHAR if --no-doublequote is specified.')
        if 'z' not in self.override_flags:
            self.argparser.add_argument('-z', '--maxfieldsize', dest='field_size_limit', type=int,
                                        help='Maximum length of a single field in the input CSV file.')
        if 'e' not in self.override_flags:
            self.argparser.add_argument('-e', '--encoding', dest='encoding', default='utf-8',
                                        help='Specify the encoding of the input CSV file.')
        if 'L' not in self.override_flags:
            self.argparser.add_argument('-L', '--locale', dest='locale', default='en_US',
                                        help='Specify the locale (en_US) of any formatted numbers.')
        if 'S' not in self.override_flags:
            self.argparser.add_argument('-S', '--skipinitialspace', dest='skipinitialspace', action='store_true',
                                        help='Ignore whitespace immediately following the delimiter.')
        if 'blanks' not in self.override_flags:
            self.argparser.add_argument('--blanks', dest='blanks', action='store_true',
                                        help='Do not convert "", "na", "n/a", "none", "null", "." to NULL.')
        if 'date-format' not in self.override_flags:
            self.argparser.add_argument('--date-format', dest='date_format',
                                        help='Specify a strptime date format string like "%%m/%%d/%%Y".')
        if 'datetime-format' not in self.override_flags:
            self.argparser.add_argument('--datetime-format', dest='datetime_format',
                                        help='Specify a strptime datetime format string like "%%m/%%d/%%Y %%I:%%M %%p".')
        if 'H' not in self.override_flags:
            self.argparser.add_argument('-H', '--no-header-row', dest='no_header_row', action='store_true',
                                        help='Specify that the input CSV file has no header row. Will create default headers (a,b,c,...).')
        if 'K' not in self.override_flags:
            self.argparser.add_argument('-K', '--skip-lines', dest='skip_lines', type=int, default=0,
                                        help='Specify the number of initial lines to skip before the header row (e.g. comments, copyright notices, empty rows).')
        if 'v' not in self.override_flags:
            self.argparser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                                        help='Print detailed tracebacks when errors occur.')

        # Output
        if 'l' not in self.override_flags:
            self.argparser.add_argument('-l', '--linenumbers', dest='line_numbers', action='store_true',
                                        help='Insert a column of line numbers at the front of the output. Useful when piping to grep or as a simple primary key.')

        # Input/Output
        if 'zero' not in self.override_flags:
            self.argparser.add_argument('--zero', dest='zero_based', action='store_true',
                                        help='When interpreting or displaying column numbers, use zero-based numbering instead of the default 1-based numbering.')

        self.argparser.add_argument('-V', '--version', action='version',
                                    version=f'{__title__}.%(prog)s ({__version__})',
                                    help='Display version information and exit.')

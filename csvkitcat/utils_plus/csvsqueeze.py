#!/usr/bin/env python


"""
Example usage:

    $ csvsqueeze -U1 examples/mess.csv


Output:

"code","name"
"1","Dan"
"02","Billy Bob"
"0003","...Who..?"
"4", "Mr. Robot"
"""

import agate
from csvkit.cli import CSVKitUtility, parse_column_identifiers
import regex as re

class squeezefoo(object):
    ORDERED_OPTS = (
        'normalize_lines',
        'squeeze_lines',
        'kill_lines',
        'normalize_spaces',
        'squeeze_spaces',
        # 'strip',
        # 'lstrip',
        # 'rstrip',
    )


    @staticmethod
    def kill_lines(text):
        """converts all newlines to plain whitespace"""
        return re.sub(r'\n', ' ', text)

    @staticmethod
    def normalize_lines(text):
        """converts all vertical whitespace characters, i.e. linebreaks, to standard newline"""
        return re.sub(r'\v', '\n', text)

    @staticmethod
    def normalize_spaces(text):
        """converts non-printable whitespace (i.e. horizontal characters) to plain whitespace"""
        return re.sub(r'\h', ' ', text)


    @staticmethod
    def squeeze_lines(text):
        """removes consecutive whitespace"""
        return re.sub(r'\n+', '\n', text)

    @staticmethod
    def squeeze_spaces(text):
        """removes consecutive whitespace"""
        return re.sub(r' +', ' ', text)


    # @staticmethod
    # def strip(text, *args):
    #     return text.strip(*args)


    # @staticmethod
    # def lstrip(text, *args):
    #     return text.lstrip(*args)

    # @staticmethod
    # def rstrip(text, *args):
    #     return text.rstrip(*args)





JUST_TEXT_COLUMNS = agate.TypeTester(types=[agate.Text(cast_nulls=False)])



class CSVSqueeze(CSVKitUtility):
    description = """Converts all space characters to a simple whitespace.
                     Squeezes consecutive whitespace.
                     Strips leading and/or trailing whitespace,
                        and/or characters of your choice"""

    override_flags = ['L', 'blanks', 'date-format', 'datetime-format']


    def add_arguments(self):
        self.argparser.add_argument('-n', '--names', dest='names_only', action='store_true',
                                    help='Display column names and indices from the input CSV and exit.')
        self.argparser.add_argument('-c', '--columns', dest='columns',
                                    help='A comma separated list of column indices, names or ranges to be extracted, e.g. "1,id,3-5". Defaults to all columns.')
        self.argparser.add_argument('-C', '--not-columns', dest='not_columns',
                                    help='A comma separated list of column indices, names or ranges to be excluded, e.g. "1,id,3-5". Defaults to no columns.')


        self.argparser.add_argument('--keep-consecutive-ws', dest='keep_consecutive_ws',
                                    action='store_true',
                                    help="""Do NOT squeeze consecutive whitespace characters into a single space""")

        self.argparser.add_argument('--keep-lines', dest='keep_lines',
                                    action='store_true',
                                    help="""Do NOT convert line breaks into simple white space""")


        # --keep-consecutive-ws
        # --keep-raw lines,spaces
        # --keep-lines
        # self.argparser.add_argument('--keep-newlines', dest='keep_newlines',
        #                             action='store_true',
        #                             help="""Do NOT convert newline characters into simple whitespace characters""")


        # self.argparser.add_argument('--keep-nonprintable-spaces', dest='keep_nonprintable_spaces',
        #                             action='store_true',
        #                             help="""Do NOT convert tabs, zero-width spaces and other such things to
        #                                 a simple whitespace""")


        # self.argparser.add_argument('-D', '--out-delimiter', dest='out_delimiter',
        #                             help='Delimiting character of the output CSV file.')
        # self.argparser.add_argument('-T', '--out-tabs', dest='out_tabs', action='store_true',
        #                             help='Specify that the output CSV file is delimited with tabs. Overrides "-D".')
        # self.argparser.add_argument('-Q', '--out-quotechar', dest='out_quotechar',
        #                             help='Character used to quote strings in the output CSV file.')
        # self.argparser.add_argument('-U', '--out-quoting', dest='out_quoting', type=int, choices=[0, 1, 2, 3],
        #                             help='Quoting style used in the output CSV file. 0 = Quote Minimal, 1 = Quote All, 2 = Quote Non-numeric, 3 = Quote None.')
        # self.argparser.add_argument('-B', '--out-no-doublequote', dest='out_doublequote', action='store_false',
        #                             help='Whether or not double quotes are doubled in the output CSV file.')
        # self.argparser.add_argument('-P', '--out-escapechar', dest='out_escapechar',
        #                             help='Character used to escape the delimiter in the output CSV file if --quoting 3 ("Quote None") is specified and to escape the QUOTECHAR if --no-doublequote is specified.')
        # self.argparser.add_argument('-M', '--out-lineterminator', dest='out_lineterminator',
        #                             help='Character used to terminate lines in the output CSV file.')



    def main(self):
        if self.args.names_only:
            self.print_column_names()
            return

        if self.additional_input_expected():
            self.argparser.error('You must provide an input file or piped data.')

        ## set arguments so that no_inference is forced
        self.args.sniff_limit = 0
        self.args.no_inference = True

        table = agate.Table.from_csv(
            self.input_file,
            skip_lines=self.args.skip_lines,
            sniff_limit=self.args.sniff_limit,
            # column_types=self.get_column_types(),
            column_types=JUST_TEXT_COLUMNS,
            **self.reader_kwargs
        )

        column_ids = parse_column_identifiers(
            self.args.columns,
            table.column_names,
            self.get_column_offset()
        )

        self.squeeze_options = []
        for key in ('consecutive_ws', 'lines',):
            argname = 'keep_%s' % key
            value = getattr(self.args, argname)
            if value:
                self.squeeze_options.append(argname)


        parsed_sqopts = self.parse_squeeze_options()
        # table = self.squeeze_table(table, self.squeeze_options)

        table = self.squeeze_table(table, column_ids, parsed_sqopts)
        table.to_csv(self.output_file, **self.writer_kwargs)




    def parse_squeeze_options(self):
        foos = list(squeezefoo.ORDERED_OPTS)
        if 'keep_consecutive_ws' in self.squeeze_options:
            foos.remove('squeeze_spaces')

        if 'keep_lines' in self.squeeze_options:
            foos.remove('kill_lines')
        print(foos)
        return foos

    def squeeze_table(self, table, column_ids, parsed_opts):
        xdata = []
        for row in table:
            d = {}
            for _x, (col, val) in enumerate(row.items()):
                d[col] = squeeze_text(val, parsed_opts) if _x in column_ids else val
                # d = {col: squeeze_text(val, parsed_opts) for col, val in row.items()}
            xdata.append(d)

        xtable = agate.Table.from_object(xdata, column_types=JUST_TEXT_COLUMNS)
        return xtable


def squeeze_text(text, methods=squeezefoo.ORDERED_OPTS):
    """cleans up a text string"""
    def _org_method_list():
        d = {}
        for k in methods:
            if type(k) is tuple:
                d[k[0]] = k[1]
            elif type(k) is str:
                d[k] = True
            else:
                raise ValueError(f"`methods` param must be a list of tuples or str, not: {k} ({type(k)})")
        return d

    newtext = text
    methods = _org_method_list()

    for key in squeezefoo.ORDERED_OPTS:
        mparams = methods.get(key)
        if mparams:
            foo = getattr(squeezefoo, key)
            newtext = foo(newtext) if mparams is True else foo(text, *mparams)

    # we always strip leading/trailing whitespace
    return newtext.strip()




def launch_new_instance():
    utility = CSVSqueeze()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()

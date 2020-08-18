#!/usr/bin/env python


r"""
Example usage:

    $ csvsed '(?i)(?:Miss|Mrs|Ms)\.? *(.+)' 'The Ms. \1' examples/honorifics-fem.csv


Output:

code,name
1,Ms. Smith
2,Ms. Daisy
3,Ms. Doe
4,Ms. Miller
5.Ms. Lee
6.Ms. maam


-----------

is equivalent to:

    printf '%s\n' 'date' '04/05/1998' | perl -p -e 's#(\d{2})/(\d{2})/(\d{4})#$3-$1-$2#g'

    printf '%s\n' 'date' '04/05/1998' | csvsed '(\d{2})/(\d{2})/(\d{4})' '\3-\1-\2'

"""

import agate
from csvkit.cli import CSVKitUtility, parse_column_identifiers
import regex as re
import warnings



JUST_TEXT_COLUMNS = agate.TypeTester(types=[agate.Text(cast_nulls=False)])


class CSVSed(CSVKitUtility):
    description = """Replaces all instances of [PATTERN] with [REPL]"""

    override_flags = ['f', 'L', 'blanks', 'date-format', 'datetime-format']


    def add_arguments(self):
        self.argparser.add_argument('-c', '--columns', dest='columns',
                                    help='A comma separated list of column indices, names or ranges to be searched, e.g. "1,id,3-5".')
        self.argparser.add_argument('-m', '--match', dest="literal_match", action='store_true',
                                    default=False,
                                    help='By default, [PATTERN] is assumed to be a regex. Set this flag to make it a literal text find/replace',)

        self.argparser.add_argument(metavar='PATTERN', dest='pattern',
                                    help='A regex pattern to find')

        self.argparser.add_argument(metavar='REPL', dest='repl',
                                    help='A regex pattern to replace with')

        self.argparser.add_argument(metavar='FILE', nargs='?', dest='input_path',
                                    help='The CSV file to operate on. If omitted, will accept input as piped data via STDIN.')

    def run(self):
        """
        A wrapper around the main loop of the utility which handles opening and
        closing files.
        """
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


        self.args.sniff_limit = 0
        self.args.no_inference = True

        table = agate.Table.from_csv(
            self.input_file,
            skip_lines=self.args.skip_lines,
            sniff_limit=self.args.sniff_limit,
            column_types=JUST_TEXT_COLUMNS,
            **self.reader_kwargs
        )

        column_ids = parse_column_identifiers(
            self.args.columns,
            table.column_names,
            self.get_column_offset()
        )


        pattern = fr'{self.args.pattern}' if self.args.literal_match else re.compile(fr'{self.args.pattern}')
        repl = fr'{self.args.repl}'

        xdata = []
        for row in table:
            d = {}
            for _x, (col, val) in enumerate(row.items()):
                if _x in column_ids:
                    d[col] = val.replace(pattern, repl)  if self.args.literal_match else pattern.sub(repl, val)
                else:
                    d[col] = val
            xdata.append(d)

        xtable = agate.Table.from_object(xdata, column_types=JUST_TEXT_COLUMNS)

        xtable.to_csv(self.output_file, **self.writer_kwargs)






def launch_new_instance():
    utility = CSVSed()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()

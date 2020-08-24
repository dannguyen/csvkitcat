#!/usr/bin/env python



from csvkitcat.alltext import AllTextUtility
import regex as re
import warnings



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



        self.argparser.add_argument('--whole', dest="whole_field_mode", action='store_true',
                                    default=False,
                                    help='Match and replace whole field',)

        self.argparser.add_argument(metavar='PATTERN', dest='pattern',
                                    help='A regex pattern to find')

        self.argparser.add_argument(metavar='REPL', dest='repl',
                                    help='A regex pattern to replace with')

        self.argparser.add_argument(metavar='FILE', nargs='?', dest='input_path',
                                    help='The CSV file to operate on. If omitted, will accept input as piped data via STDIN.')

        ###########boilerplate
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

        myio = self.init_io()

        max_match_count = self.args.max_match_count
        if max_match_count < 1: # because str.replace and re.sub use a different catchall/default value
            max_match_count = -1 if self.args.literal_match else 0

        pattern = fr'{self.args.pattern}' if self.args.literal_match else re.compile(fr'{self.args.pattern}')
        repl = fr'{self.args.repl}'

        # TK TODO THIS IS UGLY!!
        for row in myio.rows:
            d = []
            for _x, val in enumerate(row):
                if _x in myio.column_ids:
                    if self.args.whole_field_mode:
                        mx = pattern.match(val)
                        if mx:
                            partial = mx.captures(0)[0]
                            newval = pattern.sub(repl, partial)
                        else:
                            newval = val
                    else:
                        newval = val.replace(pattern, repl, max_match_count) if self.args.literal_match else pattern.sub(repl, val, max_match_count)
                else:
                    newval  = val
                d.append(newval)
            myio.output.writerow(d)


def launch_new_instance():
    utility = CSVSed()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()

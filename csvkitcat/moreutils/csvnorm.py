#!/usr/bin/env python


from csvkitcat.alltext import AllTextUtility
import regex as re

class CSVNorm(AllTextUtility):
    description = """Normalize non-printable characters, e.g. newlines, spaces, and other vertical and horizontal chars.
                     Optionally, normalize letter case"""

    override_flags = [ 'S', 'L', 'blanks', 'date-format', 'datetime-format']



    def add_arguments(self):
        self.argparser.add_argument('-n', '--names', dest='names_only', action='store_true',
                                    help='Display column names and indices from the input CSV and exit.')
        self.argparser.add_argument('-c', '--columns', dest='columns',
                                    help='A comma separated list of column indices, names or ranges to be extracted, e.g. "1,id,3-5". Defaults to all columns.')

        self.argparser.add_argument('-T', '--translations', dest='tr_actions',
                    action='append',
                    choices=Normy.TR_ACTIONS.copy(),
                    default=[],
                    help='''A list of "space" character translations. By default, all of the following are performed:

                    "(h)orizontal" converts all line-break/newline, and other vertical characters to: "\n"

                    "(v)ertical" converts all whitespace/tab/zero-width and other horizontal characters to simple whitespace, i.e. " "
                    ''')

        self.argparser.add_argument('--TX', '--no-translate-space', dest='tr_actions_disabled',
                    action='store_true',
                    help='''Do no space character translations, i.e. ignore and override -T/--translate-space option''')


        self.argparser.add_argument('-S', '--squeeze', dest='squeeze_actions',  action='append',
                   choices=Normy.SQUEEZE_ACTIONS.copy(),
                   default=[],
                   help='''A list of consecutive space squeezing/collapsing actions. By default, all of the following are performed:

                    "(l)ines" squeezes consecutive '\n' characters
                    "(s)paces" squeezes consecutive ' ' characters''')

        self.argparser.add_argument('--SX', '--no-squeeze', dest='squeeze_actions_disabled',
                    action='store_true',
                    help='''Do no consecutive space squeezing i.e. ignore and override -S/--squeeze''')


        self.argparser.add_argument('--keep-lines', dest='dont_convert_lines', action='store_true',
                    help=r'''Disable the default behavior of converting all "\n" characters
                    are converted to plain white space, i.e. " ".''')


        self.argparser.add_argument('-C', '--change-case', dest='change_case',
                    choices=('upper', 'lower', 'none'),
                    default='none',
                    help=r"""Apply "upper" or "lower" casing to values.""")

        self.argparser.add_argument('--no-strip', dest='dont_strip', action='store_true', default=False,
            help=r'''Disable the default behavior of stripping leading and trailing "\s" characters from value fields''')



    def main(self):


        if self.args.names_only:
            self.print_column_names()
            return

        if self.additional_input_expected():
            self.argparser.error('You must provide an input file or piped data.')

        # parse normalization options
        self.normalization_opts = ops = {}

         # TK whatever TODO fix later
        if self.args.tr_actions_disabled:
            ops['tr_actions'] = None
        elif not self.args.tr_actions: # i.e. empty array
            ops['tr_actions'] = Normy.TR_ACTIONS
        else:
            ops['tr_actions'] = list(set(self.args.tr_actions))


        if self.args.squeeze_actions_disabled:
            ops['squeeze_actions'] = None
        elif not self.args.squeeze_actions: # i.e. empty array
            ops['squeeze_actions'] = Normy.SQUEEZE_ACTIONS
        else:
            ops['squeeze_actions'] = list(set(self.args.squeeze_actions))


        ops['change_case'] = False if self.args.change_case in ('none', None) else self.args.change_case
        ops['convert_lines'] = False if self.args.dont_convert_lines else True
        ops['strip'] = False if self.args.dont_strip else True


        myio = self.init_io()

        for row in myio.rows:
            for i, val in enumerate(row):
                if i in myio.column_ids:
                    row[i] = Normy.norm(val, self.normalization_opts)
            myio.output.writerow(row)

        # import json
        # print("normalize operations:", json.dumps(self.normalization_opts, indent=2))



class Normy(object):

    TR_ACTIONS_META = {
        'h': 'horizontal',
        'v': 'vertical',
    }

    SQUEEZE_ACTIONS_META = {
        'l': 'lines',
        's': 'spaces',
    }

    TR_ACTIONS = list(TR_ACTIONS_META.keys())
    SQUEEZE_ACTIONS = list(SQUEEZE_ACTIONS_META.keys())


    @staticmethod
    def norm(txt, options):
        # space actions
        _ops = options.get('tr_actions')
        if _ops:
            if 'v' in _ops:
                txt =  re.sub(r'\v', '\n', txt)
            if 'h' in _ops:
                txt = re.sub(r'\h', ' ', txt)

        # convert lines
        if options.get('convert_lines') is True:
            txt = re.sub(r'\n', ' ', txt)

        # squeeze actions
        _ops = options.get('squeeze_actions')
        if _ops:
            if 'l' in _ops:
                txt =  re.sub(r'\n+', '\n', txt)
            if 's' in _ops:
                txt = re.sub(r' +', ' ', txt)

        cc = options.get('change_case')
        if cc:
            txt = txt.lower() if cc == 'lower' else txt.upper()

        txt = txt.strip() if options.get('strip') is True else txt
        return txt






def launch_new_instance():
    utility = CSVNorm()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()

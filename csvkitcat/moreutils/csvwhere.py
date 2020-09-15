import argparse
import csv
from io import StringIO
import sys
from typing import NoReturn as typeNoReturn, Union as typeUnion,  Tuple as typeTuple
from typing import List as typeList, Dict as typeDict, Callable as typeCallable
import warnings

from csvkitcat import agate, rxlib as re, parse_column_identifiers
from csvkitcat.kitcat.agatable import AgatableUtil, parse_aggregate_string_arg, print_available_aggregates

VALID_OPERATORS = {
    'eq': '==',
    'gt' : '>',
    'gte': '>=',
    'lt': '<',
    'lte': '<=',
    'neq': '!=',
}

ALLOWED_TYPECASTS = ('number', 'time', 'text', 'auto',)



TIME_PARSER = agate.data_types.DateTime()

def time_parse(dt:str):
    return TIME_PARSER.cast(dt)


def strict_time_parse(dt:str):
    if re.match(r'\d{4}.d{2}.d{2}', dt):
        return time_parse(dt)
    else:
        raise ValueError(f"{dt} is probably not a datetime value")

def _rough_cast_value(value, datatype):
    if datatype == 'number':
        newval = float(value)
    elif datatype == 'time':
        newval = time_parse(value)
    elif datatype == 'auto':
        for foo in (float, strict_time_parse, str):
            try:
                tv = foo(value)
            except Exception as err:
                newval = value
            else:
                newval = tv
                break
    elif datatype == 'str': # TK
        newval = str(_val)
    else:
        raise ValueError(f'Unexpected datatype: {datatype}')
    return newval


def parse_value_type_arg(line:str) -> typeUnion[typeDict[str, str], bool]:
    """expects something like: '2020' or '2020|date' or '2020|text' """
    df = { 'operator': None, 'operand': None, 'datatype': None,}
    src = StringIO(line)
    valstring, *dt = next(csv.reader(src, delimiter='|'))
    if len(dt) == 0:
        df['datatype'] = 'auto'
    elif len(dt) == 1:
        if dt[0] not in ALLOWED_TYPECASTS:
            # then this is some other weird string; return False
            return False
            # raise ValueError(f"Unexpected TKTK val arg: {d[0]}")
        else:
            df['datatype'] = dt[0]
    else:
       # raise ValueError(f"Unexpected TKTK val arg: {line}")
       return False

    valstring = valstring.strip()
    _op = next( (v for v in [valstring[0:2], valstring[0]] if v in VALID_OPERATORS.values()), False)
    if not _op:
        return False
    else:
        df['operator'] = _op
        df['operand'] = valstring.split(_op, 1)[1].strip()
        return df



    # if _op in VALID_OPERATORS.values():
    #     df['operator'] = _op
    #     _val = valstring[2:].strip()

    #     if df['datatype'] == 'number':
    #         df['operand'] = float(_val)
    #     elif df['datatype'] == 'time':
    #         df['operand'] = time_parse(_val)
    #     elif df['datatype'] == 'auto':
    #         cv = _val
    #         for t in (float, strict_time_parse, str):
    #             try:
    #                 tv = t(_val)
    #             except Exception as err:
    #                 cv = _val
    #             else:
    #                 cv = tv
    #                 break
    #         df['operand'] = cv


    #     else: # TK
    #         df['operand'] = str(_val)
    #     return df
    # else:
    #     return False





class CSVWhere(AgatableUtil):
    description = """Do the equivalent of a SQL WHERE"""

    override_flags = ['f' , 'L', 'blanks', 'date-format', 'datetime-format']


    def add_arguments(self):

        self.argparser.add_argument('-y', '--snifflimit', dest='sniff_limit', type=int,
                                    help='Limit CSV dialect sniffing to the specified number of bytes. Specify "0" to disable sniffing entirely.')
        self.argparser.add_argument('-I', '--no-inference', dest='no_inference', action='store_true',
                                    help='Disable type inference when parsing the input.')



        self.argparser.add_argument(metavar='COLUMNS', dest='columns_first_expr', type=str,
                                    help='a comma-delimited list of columns',)


        self.argparser.add_argument(metavar='CONDITIONAL', dest='conditional_first_expr', type=str,
                                    help='a conditional statement, like ">= 9|number"',)



        self.argparser.add_argument('-A', '--and', nargs='*', dest='additional_statements', action=AppendConditionalAction, help='AND conditional')
        self.argparser.add_argument('-O', '--or', nargs='*', dest='additional_statements', action=AppendConditionalAction, help='OR conditional')



        self.argparser.add_argument(metavar='FILE', nargs='?', dest='input_path',
                                    help='The CSV file to operate on. If omitted, will accept input as piped data via STDIN.')


    def handle_standard_args(self):
        # if self.additional_input_expected():
        #     self.argparser.error('You must provide an input file or piped data.')
        pass

    def handle_statements(self) -> typeList[typeTuple]:
        statements = []
        columns_str = self.args.columns_first_expr

        first_state = {'bool_type': 'FIRST', 'columns': columns_str}
        first_state.update(parse_value_type_arg(self.args.conditional_first_expr))
        statements.append(first_state)

        if self.args.additional_statements:
            for c in self.args.additional_statements.copy():

                if c['columns'] is not None:
                    columns_str = c['columns']
                else:
                    c['columns'] = columns_str
                statements.append(c)
                # op, _col, _valstr = c

            # val, dtype = parse_value_type_arg(_valstr)

            # statements.append([op, columns_str, val, dtype])

        return statements


    def main(self):

        self.statements = self.handle_statements()
        self.handle_standard_args()


        # _input_name = self.args.input_path if self.args.input_path else 'stdin'
        # sys.stderr.write(f'{_input_name=}\n')





        def _build_conditional_foo(column_names, operator, operand, idnum) -> typeTuple:
            """
            returns:

                'all(row[col] [OPERATOR] [OPERAND] for col in column_names)', {column_names_idnum: column_names operator_idnum=operator, operand_idnum=operand}
            """
            operand_label = f"operand_{idnum}"
            colnames_label = f"column_names_{idnum}"
            funcstr = f"""all(row[col] {operator} {operand_label} for col in {colnames_label})"""
            funclocals = {operand_label: operand, colnames_label: column_names}
            return (funcstr, funclocals)


        rawtable = agate.Table.from_csv(
            self.input_file,
            skip_lines=self.args.skip_lines,
            sniff_limit=self.args.sniff_limit,
            **self.reader_kwargs
        )

        column_names = rawtable.column_names


        # _input_name = self.args.input_path if self.args.input_path else 'stdin'
        # sys.stderr.write(f'{_input_name=}\n')

        # sys.stderr.write("Statements:\n")
        # for c in self.statements:
        #     sys.stderr.write(f"\t{c}\n")

        func_str = ""
        func_locals = {}




        for i, state in enumerate(self.statements):
            _col_ids = parse_column_identifiers(
                state['columns'],
                column_names,
                column_offset=self.get_column_offset(),
                excluded_columns=None
            )
            state_colnames = [column_names[i] for i in _col_ids] if _col_ids else None
            if not state_colnames:
                raise ValueError(f"Did not find valid column names in: {state['columns']}")


            opvalue = _rough_cast_value(state['operand'], state['datatype'])

            fstr, flocals = _build_conditional_foo(state_colnames, state['operator'], opvalue, i)

            func_str += fstr if state['bool_type'] == 'FIRST' else f" {state['bool_type'].lower()} {fstr}"
            func_locals.update(flocals)




        # sys.stderr.write(f'{func_str=}\n\n')
        # for k, v in func_locals.items():
        #     sys.stderr.write(f'{k}: {v}\n')


        xrows = []

        if rawtable._row_names is not None:
            rrow_names = []
        else:
            rrow_names = None

        for i, row in enumerate(rawtable._rows):
            row_locals = func_locals.copy()
            row_locals.update({'row': row})
            test_row = eval(func_str, row_locals)
            if test_row:
                xrows.append(row)

                if rrow_names is not None:
                    rrow_names.append(rawtable._row_names[i])

        xtable = rawtable._fork(xrows, row_names=rrow_names)
        # xtable = xtable.where(lambda row: )
        #     # xtable = gtable.aggregate(g_aggs)
        xtable.to_csv(self.output_file, **self.writer_kwargs)




    def run(self):
        """
        A wrapper around the main loop of the utility which handles opening and
        closing files.

        TK: This is copy-pasted form CSVKitUtil because we have to override 'f'; maybe there's
            a way to refactor this...
        """


        if not self.args.input_path:
            if self.args.additional_statements:
                # this is before handle_statements() is called, so each statement is at a
                # minimum of 2 args, e.g. ['OR', '> 10']
                # and max 3, e.g. ['OR', 'col_1,col_2', '>10']
                last_state = self.args.additional_statements[-1]
                if last_state['extra_args']:
                    self.args.input_path = last_state['extra_args'][0]



        #     if len(self.last_expr) > 2:
        #         # could be either 3 or 4
        #         self.args.input_path = self.last_expr.pop()
        #     elif len(self.last_expr) == 2:
        #         pass
        #         # do nothing, but be warned that if there is no stdin,
        #         # then -E might have eaten up the input_file argument
        #         # and interpreted it as pattern
        #     else:
        #         # else, last_expr has an implied third argument, and
        #         # input_path is hopefully stdin
        #         self.args.input_path = None


        self.input_file = self._open_input_file(self.args.input_path)

        try:
            with warnings.catch_warnings():
                if getattr(self.args, 'no_header_row', None):
                    warnings.filterwarnings(action='ignore', message='Column names not specified', module='agate')

                self.main()
        finally:
            self.input_file.close()

def launch_new_instance():
    utility = CSVWhere()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()





class AppendConditionalAction(argparse.Action):

    def __init__(self,
                 option_strings,
                 dest,
                 nargs=None,
                 const=None,
                 default=None,
                 type=None,
                 choices=None,
                 required=False,
                 help=None,
                 metavar='STATEMENT'):
        if nargs == 0:
            raise ValueError('nargs for append actions must be != 0; if arg '
                             'strings are not supplying the value to append, '
                             'the append const action may be more appropriate')
        if const is not None and nargs != argparse.OPTIONAL:
            raise ValueError('nargs must be %r to supply const' % argparse.OPTIONAL)
        super(AppendConditionalAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            const=const,
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest, None)
        items = argparse._copy_items(items)

        if len(values) < 1:
            raise ValueError(f'TK: statement must contain at least 1 argument')

        # if len(values) == 1:
        #     newvals = [None] + values
        # else:
        #     newvals = values

        df = {'bool_type': None, 'columns': None, 'operator':None, 'operand': None, 'datatype': None, 'extra_args': []}
        df['bool_type'] = self.option_strings[1].lstrip('-').upper()


        for i, val in enumerate(values):
            valobj = parse_value_type_arg(val)
            if valobj:
                if i >= 1:
                    df['columns'] = values[i - 1]
                df.update(valobj)
                df['extra_args'] = values[i+1:]
                break
            else:
                pass

        # if len(values) == 1:
        #     valobj = parse_value_type_arg(values[0])
        # else:


        #     raise ValueError(f'TK: value arg for last statement seems to be invalid: {values[-1]}')
        # else:

        #     # then we assume no columns is specified, just a value_datatype str
        #     d['operand'], d['datatype'] = parse_value_type_arg(values[0])
        # if

        # newvals = [ctype] + values

        items.append(df)
        setattr(namespace, self.dest, items)

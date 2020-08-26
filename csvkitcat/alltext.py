import agate
from collections import namedtuple
import six

from csvkitcat import CSVKitcatUtil


# JUST_TEXT_COLUMNS = agate.TypeTester(types=[agate.Text(cast_nulls=False)])


MyIO = namedtuple('MyIO', ['rows', 'column_names', 'column_ids', 'output',])

class AllTextUtility(CSVKitcatUtil):

    def init_io(self, write_header=True):
        self.args.sniff_limit = 0       # TK is needed??
        self.args.no_inference = True   # TK is needed??

        if not hasattr(self.args, 'columns'):
            self.args.columns = []

        rows, column_names, column_ids = self.get_rows_and_column_names_and_column_ids(**self.reader_kwargs)

        output = agate.csv.writer(self.output_file, **self.writer_kwargs)
        if write_header is True:
            output.writerow(column_names)

        return MyIO(rows=rows, column_names=column_names, column_ids=column_ids, output=output)


    # copied from csvkit.cli.CSVKitUtility
    # removes breakage at:
    #    value = getattr(self.args, arg)
    # by changing to:
    #    value = getattr(self.args, arg, None)
    def _extract_csv_reader_kwargs(self):
        """
        Extracts those from the command-line arguments those would should be passed through to the input CSV reader(s).
        """
        kwargs = {}

        if self.args.tabs:
            kwargs['delimiter'] = '\t'
        elif self.args.delimiter:
            kwargs['delimiter'] = self.args.delimiter

        for arg in ('quotechar', 'quoting', 'doublequote', 'escapechar', 'field_size_limit', 'skipinitialspace'):
            value = getattr(self.args, arg, None)
            if value is not None:
                kwargs[arg] = value

        if six.PY2 and self.args.encoding:
            kwargs['encoding'] = self.args.encoding

        if getattr(self.args, 'no_header_row', None):
            kwargs['header'] = not self.args.no_header_row

        return kwargs

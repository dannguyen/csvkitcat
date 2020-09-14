import agate
from collections import namedtuple
import six

from csvkitcat.kitcat.ckutil import CSVKitcatUtil
from sys import stdout

# JUST_TEXT_COLUMNS = agate.TypeTester(types=[agate.Text(cast_nulls=False)])


MyIO = namedtuple('MyIO', ['rows', 'column_names', 'column_ids', 'output',])

class JustTextUtility(CSVKitcatUtil):

    def init_io(self, write_header=True):

        if not hasattr(self.args, 'columns'):
            self.args.columns = []

        rows, column_names, column_ids = self.get_rows_and_column_names_and_column_ids(**self.reader_kwargs)

        output = agate.csv.writer(self.output_file, **self.writer_kwargs)
        if write_header is True:
            output.writerow(column_names)

        return MyIO(rows=rows, column_names=column_names, column_ids=column_ids, output=output)


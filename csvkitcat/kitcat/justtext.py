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

        reader_kwargs = self.reader_kwargs
        writer_kwargs = self.writer_kwargs

        # Move the line_numbers option from the writer to the reader.
        if writer_kwargs.pop("line_numbers", False):
            reader_kwargs["line_numbers"] = True


        rows, column_names, column_ids = self.get_rows_and_column_names_and_column_ids(**reader_kwargs)

        output = agate.csv.writer(self.output_file, **writer_kwargs)
        if write_header is True:
            output.writerow(column_names)

        return MyIO(rows=rows, column_names=column_names, column_ids=column_ids, output=output)


import agate
from csvkit.cli import CSVKitUtility, parse_column_identifiers
from collections import namedtuple


# JUST_TEXT_COLUMNS = agate.TypeTester(types=[agate.Text(cast_nulls=False)])


MyIO = namedtuple('MyIO', ['rows', 'column_names', 'column_ids', 'output',])

class AllTextUtility(CSVKitUtility):

    def init_io(self):
        self.args.sniff_limit = 0       # TK is needed??
        self.args.no_inference = True   # TK is needed??

        if not self.args.columns:
            self.args.columns = []

        rows, column_names, column_ids = self.get_rows_and_column_names_and_column_ids(**self.reader_kwargs)

        output = agate.csv.writer(self.output_file, **self.writer_kwargs)
        output.writerow(column_names)

        return MyIO(rows=rows, column_names=column_names, column_ids=column_ids, output=output)

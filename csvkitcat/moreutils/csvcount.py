from collections import defaultdict
import csv
import regex as re

from csvkitcat.alltext import AllTextUtility

class _keydict(defaultdict):
    """
    esoteric thingy: https://stackoverflow.com/a/2912455/160863
    """
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError( key )
        else:
            ret = self[key] = self.default_factory(key)
            return ret

def count_csv_rows(file, no_headers=False):
    c = csv.reader(file)
    if not no_headers:
        headers = next(c)
    else:
        headers = None

    xc = sum(1 for r in c)
    return xc

class CSVCount(AllTextUtility):
    description = """Returns count of rows, not counting header. Much much MUCH slower than `xsv count`
    It's even slower than `csvstat --count` ¯\\_(ツ)_/¯"""

    # override_flags = [ 'S', 'P', 'zero',  'l', 'L', 'blanks', 'date-format', 'datetime-format']
    override_flags = [ 'P', 'S', 'L', 'blanks', 'date-format', 'datetime-format']


    def add_arguments(self):

        self.argparser.add_argument('-P', '--patterns', dest="patterns",
                                    action='append',
                                    type=str,
                                    help='TKTK list of patterns',)

        self.argparser.add_argument('-c', '--columns', dest='columns',
                                    help='A comma separated list of column indices, names or ranges to be searched, e.g. "1,id,3-5".')

    def main(self):

        if self.additional_input_expected():
            self.argparser.error('You must provide an input file or piped data.')

        myio = self.init_io(write_header=False)


        # TODO: refactor this spaghetti ass code
        if not self.args.patterns:
            header = ['rows', 'cells', 'empty_rows', 'empty_cells', 'blank_lines']
            myio.output.writerow(header)
            # iterate through each row, since we need to count cells
            dd = {k: 0 for k in header}
            ncols = len(myio.column_ids)
            for i, row in enumerate(myio.rows):
                if not row: # i.e. a blank line
                    dd['blank_lines'] += 1
                else:
                    dd['rows'] += 1
                    row_empty_cell_count = 0
                    for j, cell in enumerate(row):
                        if j in myio.column_ids:
                            dd['cells'] += 1
                            if cell == '':
                                row_empty_cell_count += 1

                    dd['empty_cells'] += row_empty_cell_count
                    if row_empty_cell_count == ncols: # consider the row a blank
                        dd['empty_rows'] += 1

            myio.output.writerow(dd.values())


        else:
            patterns = [re.compile(p) for p in self.args.patterns]
            header = ['pattern', 'rows', 'cells', 'matches']
            myio.output.writerow(header)

            tally = _keydict(lambda x: {'pattern': x.pattern, 'rows': 0, 'cells': 0, 'matches': 0})

            for i, row in enumerate(myio.rows):
                for p in patterns:
                    is_row_matched = False
                    for j, cell in enumerate(row):
                        if j in myio.column_ids:
                            matches = p.findall(cell)
                            if matches:
                                is_row_matched = True
                                tally[p]['cells'] += 1
                                tally[p]['matches'] += len(matches)
                    if is_row_matched:
                        tally[p]['rows'] += 1
#            print(tally.items())
            for p in patterns:
                t = tally[p]
                myio.output.writerow(t.values()) # maybe I should do DictWriter??

def launch_new_instance():
    utility = CSVCount()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()

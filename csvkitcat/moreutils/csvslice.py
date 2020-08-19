
from csvkitcat.alltext import AllTextUtility
from csvkitcat.exceptions import ArgumentErrorTK
import regex as re
import warnings
from sys import stderr

class CSVSlice(AllTextUtility):
    description = """Returns the header, plus rows in the specified 0-index range, half-open-interval"""

    override_flags = [ 'S', 'L', 'blanks', 'date-format', 'datetime-format']


    def add_arguments(self):
        self.argparser.add_argument('-S', '--start', dest='slice_start',
                                    type=int,
                                    help="0-index position of record to start slicewith",)

        self.argparser.add_argument('-E', '--end', dest="slice_end",
                                    type=int,
                                    help="0-index position of record to end slice with",)

        self.argparser.add_argument('-L', '--len', dest="slice_length",
                                    type=int,
                                    help="Length of slice. Incompatible with -E/--end",)

        self.argparser.add_argument('-i', '--index', dest='slice_index',
                                    type=int,
                                    help='0-based index of single record to slice and extract; Short for `--start [INDEX} --length 1`')

    def main(self):
        if self.additional_input_expected():
            self.argparser.error('You must provide an input file or piped data.')

        if all(a is None for a in (self.args.slice_start, self.args.slice_end, self.args.slice_length, self.args.slice_index)):
            raise ArgumentErrorTK(f'At least 1 of (start, end, length, index) must be non-null')

        if self.args.slice_index and any(a is not None for a in (self.args.slice_start, self.args.slice_end, self.args.slice_length,)):
            raise ArgumentErrorTK('Slice index cannot be set if start/end/length are also defined')
        if self.args.slice_end is not None and self.args.slice_length is not None:
            raise ArgumentErrorTK(f'Cannot set both `slice_end` {self.args.slice_end} AND `slice_length` {self.args.slice_length}')

        # if self.args.slice_start and self.args.slice_end and self.args.slice_start >= self.args.slice_end:
        #     raise ArgumentErrorTK(f'`slice_start` {self.args.slice_start} must be less than `slice_end` {self.args.slice_end}')



        if self.args.slice_index is not None: # --index mode
            slice_start = self.args.slice_index
            slice_end = slice_start + 1
        elif not self.args.slice_length: # no slice length, and either start or end or set
            slice_start = self.args.slice_start if self.args.slice_start else None
            slice_end = self.args.slice_end if self.args.slice_end else None
            # (impossible at this point for slice_start/end/length and index to be None)
        else:
            # assume slice_length AND slice_start is set
            # as it's impossible for slice_length and slice_end to co-exist
            slice_start = self.args.slice_start if self.args.slice_start else 0
            slice_end = slice_start + self.args.slice_length


        myio = self.init_io()
        rowslice = list(myio.rows)[slice_start:slice_end] ## TKTK VERY BAD CODE
        for i, row in enumerate(rowslice):
            myio.output.writerow(row)


def launch_new_instance():
    utility = CSVSlice()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()

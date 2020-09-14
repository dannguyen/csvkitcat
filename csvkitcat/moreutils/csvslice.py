
from csvkitcat.kitcat.justtext import JustTextUtility
from csvkitcat.exceptions import ArgumentErrorTK
from csvkitcat import rxlib as re

import warnings
from sys import stderr

class CSVSlice(JustTextUtility):
    description = """Returns the header, plus rows in the specified 0-index range, half-open-interval"""

    override_flags = ['L', 'blanks', 'date-format', 'datetime-format']


    def add_arguments(self):
        self.argparser.add_argument('-B', '--begin', dest='slice_begin',
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
                                    help='0-based index of single record to slice and extract; Short for `--begin [INDEX} --length 1`')

    def main(self):
        if self.additional_input_expected():
            self.argparser.error('You must provide an input file or piped data.')

        if all(a is None for a in (self.args.slice_begin, self.args.slice_end, self.args.slice_length, self.args.slice_index)):
            raise ArgumentErrorTK(f'At least 1 of (start, end, length, index) must be non-null')

        if self.args.slice_index and any(a is not None for a in (self.args.slice_begin, self.args.slice_end, self.args.slice_length,)):
            raise ArgumentErrorTK('Slice index cannot be set if start/end/length are also defined')
        if self.args.slice_end is not None and self.args.slice_length is not None:
            raise ArgumentErrorTK(f'Cannot set both `slice_end` {self.args.slice_end} AND `slice_length` {self.args.slice_length}')

        # if self.args.slice_begin and self.args.slice_end and self.args.slice_begin >= self.args.slice_end:
        #     raise ArgumentErrorTK(f'`slice_begin` {self.args.slice_begin} must be less than `slice_end` {self.args.slice_end}')



        if self.args.slice_index is not None: # --index mode
            slice_begin = self.args.slice_index
            slice_end = slice_begin + 1
        elif not self.args.slice_length: # no slice length, and either start or end or set
            slice_begin = self.args.slice_begin if self.args.slice_begin else None
            slice_end = self.args.slice_end if self.args.slice_end else None
            # (impossible at this point for slice_begin/end/length and index to be None)
        else:
            # assume slice_length AND slice_begin is set
            # as it's impossible for slice_length and slice_end to co-exist
            slice_begin = self.args.slice_begin if self.args.slice_begin else 0
            slice_end = slice_begin + self.args.slice_length


        myio = self.init_io()
        rowslice = list(myio.rows)[slice_begin:slice_end] ## TKTK VERY BAD CODE
        for i, row in enumerate(rowslice):
            myio.output.writerow(row)


def launch_new_instance():
    utility = CSVSlice()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()

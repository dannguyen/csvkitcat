
from csvkitcat.alltext import AllTextUtility
from csvkitcat.exceptions import ArgumentErrorTK
import regex as re
import warnings


class CSVSlice(AllTextUtility):
    description = """Returns the header, plus rows in the specified 0-index range, half-open-interval"""

    override_flags = [ 'L', 'blanks', 'date-format', 'datetime-format']


    def add_arguments(self):
        self.argparser.add_argument('--is', '--start', dest='slice_start',
                                    type=int,
                                    help="start",)

        self.argparser.add_argument('--ie', '--end', dest="slice_end",
                                    type=int,
                                    help="end",)

        self.argparser.add_argument('--len', dest="slice_length",
                                    type=int,
                                    help="length",)


    def main(self):
        if self.additional_input_expected():
            self.argparser.error('You must provide an input file or piped data.')


        if self.args.slice_end is not None and self.args.slice_length is not None:
            raise ArgumentErrorTK(f'Cannot set both `slice_end` {self.args.slice_end} AND `slice_length` {self.args.slice_length}')

        # if self.args.slice_start and self.args.slice_end and self.args.slice_start >= self.args.slice_end:
        #     raise ArgumentErrorTK(f'`slice_start` {self.args.slice_start} must be less than `slice_end` {self.args.slice_end}')


        slice_start = self.args.slice_start if self.args.slice_start else 0
        slice_length = self.args.slice_length if self.args.slice_length else 0

        if self.args.slice_end:
            slice_end = self.args.slice_end
        else:
            if slice_length == 0:
                slice_end = None
            else:
                slice_end = slice_start + slice_length

#        print(f"slice start: {slice_start}; slice end: {slice_end}")

        myio = self.init_io()
        rowslice = list(myio.rows)[slice_start:slice_end] ## TKTK VERY BAD CODE
        for i, row in enumerate(rowslice):
            myio.output.writerow(row)


def launch_new_instance():
    utility = CSVSlice()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()

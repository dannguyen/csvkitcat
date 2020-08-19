
from csvkitcat.alltext import AllTextUtility
import regex as re
import warnings



class CSVSlice(AllTextUtility):
    description = """Returns the header, plus rows in the specified 0-index range"""

    override_flags = [ 'L', 'blanks', 'date-format', 'datetime-format']


    def add_arguments(self):
        self.argparser.add_argument('--is', '--start', dest='slice_start',
                                    default=0,
                                    type=int,
                                    help="start",)

        self.argparser.add_argument('--ie', '--end', dest="slice_end",
                                    default=-1,
                                    type=int,
                                    help="end",)

        self.argparser.add_argument('--il', '--len', dest="slice_len",
                                    default=0,
                                    type=int,
                                    help="length",)


    def main(self):
        pass


def launch_new_instance():
    utility = CSVSlice()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()

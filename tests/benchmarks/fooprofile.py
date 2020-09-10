#!/usr/bin/env python3
"""
baby's try at using cProfile!
"""


from csvkit.utilities.csvgrep import CSVGrep
from csvkitcat.moreutils.csvsed import CSVSed


from io import StringIO
from pathlib import Path
import cProfile

import sys

SRC_PATH = str(Path("ZUNK/mass-fec.csv"))


def grep():
    grepio = StringIO()
    grepargs = ["-a", "-c", "1-77", "-r", "TRUMP|BIDEN", SRC_PATH]
    grep = CSVGrep(grepargs, grepio)
    grep.run()
    grep_output = grepio.getvalue()
    grep_lines = grep_output.splitlines()


#    print(f"CSVGrep found {len(grep_lines)} lines")


def sed():
    io = StringIO()
    vargs = ["-c", "1-77", "TRUMP|BIDEN", "NONE", SRC_PATH]
    util = CSVSed(vargs, io)
    util.run()
    output = io.getvalue()
    lines = output.splitlines()


if __name__ == "__main__":
    # print(timeit.timeit("tgrep()", setup="from __main__ import tgrep", number=10))
    fooname = sys.argv[1]
    cProfile.run(f"{fooname}()")

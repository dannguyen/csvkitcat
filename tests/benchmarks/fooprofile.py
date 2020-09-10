#!/usr/bin/env python3
"""
baby's try at using cProfile!
"""


from csvkit.utilities.csvgrep import CSVGrep
from csvkitcat.moreutils.csvsed import CSVSed
from csvkitcat.moreutils.csvrgrep import CSVRgrep


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


def rgrep():
    io = StringIO()
    vargs = ["-c", "1-77", "-E", "TRUMP|BIDEN", SRC_PATH]
    util = CSVRgrep(vargs, io)
    util.run()
    output = io.getvalue()
    lines = output.splitlines()


#    print(f"CSVGrep found {len(grep_lines)} lines")


def sed():
    io = StringIO()
    vargs = ["-G", "-c", "1-77", "TRUMP|BIDEN", "DOODLES", SRC_PATH]
    util = CSVSed(vargs, io)
    util.run()
    output = io.getvalue()
    lines = output.splitlines()


if __name__ == "__main__":
    # print(timeit.timeit("tgrep()", setup="from __main__ import tgrep", number=10))
    fooname = sys.argv[1]
    print(f"Profiling: {fooname}")
    cProfile.run(f"{fooname}()")

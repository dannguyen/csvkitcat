#!/usr/bin/env python3

r"""

just a quickie test;


    time tests/benchmarks/rawsed.py raw  > /dev/null

        real    0m0.307s
        user    0m0.237s
        sys 0m0.061s

    time tests/benchmarks/rawsed.py csv  > /dev/null
        real    0m0.646s
        user    0m0.553s
        sys     0m0.082s


Compare to:



    time csvsed '(\d{4})-(\d{2})-(\d{2})' '\2/\3/\1' \
        examples/realdata/osha-violation.csv > /dev/null

        real    0m1.153s
        user    0m1.003s
        sys 0m0.136s

Or:

    time perl -p -e 's#(\d{2})/(\d{2})/(\d{4})#$3-$1-$2#g' \
      examples/realdata/osha-violation.csv > /dev/null

        real    0m0.028s
        user    0m0.017s
        sys 0m0.007s

"""

from sys import argv, stdout, stderr
import csv
import regex as re

DEFAULT_PATH = 'examples/realdata/osha-violation.csv'
DEFAULT_PATTERN = re.compile(r'(\d{4})-(\d{2})-(\d{2})')
DEFAULT_REPL = r'\2/\3/\1'

def as_csv(inpath):
    stderr.write("mode: as_csv\n")

    outs = csv.writer(stdout)

    with open(inpath) as src:
        for row in csv.reader(src):
            d = []
            for col in row:
                d.append(DEFAULT_PATTERN.sub(DEFAULT_REPL , col))
            outs.writerow(d)


def as_raw(inpath):
    stderr.write("mode: as_raw\n")
    with open(inpath) as src:
        for line in src:
            xline = DEFAULT_PATTERN.sub(DEFAULT_REPL, line)
            stdout.write(xline)

if __name__ == '__main__':
    inpath = DEFAULT_PATH if len(argv) < 3 else argv[2]

    if len(argv) > 1:
        if argv[1] == 'raw':
           as_raw(inpath)
        else:
            as_csv(inpath)
    else:
        as_csv(inpath)


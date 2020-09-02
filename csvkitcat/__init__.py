#!/usr/bin/env python

"""
This module contains csvkit's superpowered alternative to the standard Python
CSV reader and writer. It can be used as a drop-in replacement for the standard
module.

.. warn::

    Since version 1.0 csvkit relies on `agate <http://agate.rtfd.org>`_'s
CSV reader and writer. This module is supported for legacy purposes only and you
should migrate to using agate.
"""

import agate

reader = agate.csv.reader
writer = agate.csv.writer
DictReader = agate.csv.DictReader
DictWriter = agate.csv.DictWriter

from csvkit.cli import CSVKitUtility, parse_column_identifiers

from slugify import slugify as pyslugify
from typing import Union as tyUnion, Sequence as tySequence



def slugify(txt:tyUnion[str, tySequence]):
    if not isinstance(txt, str):
        txt = ' '.join(txt)
    return pyslugify(txt, separator='_')


class CSVKitcatUtil(CSVKitUtility):
    def get_column_offset(self):
        if getattr(self.args, 'zero_based', None):
            if self.args.zero_based:
                return 0
            else:
                return 1
        else:
            return 1
    # dumb hack

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
agate = agate

#  from csvkit import reader, writer, DictReader, DictWriter
from csvkit.cli import CSVKitUtility, parse_column_identifiers
from csvkitcat.__about__ import  __title__, __version__


from slugify import slugify as pyslugify
from typing import Union as tyUnion, Sequence as tySequence



import re as _rxlib  # because I'm still deciding between re/regex, we should have a global reference to the lib
rxlib = _rxlib



def slugify(txt:tyUnion[str, tySequence]):
    if not isinstance(txt, str):
        txt = ' '.join(txt)
    return pyslugify(txt, separator='_')


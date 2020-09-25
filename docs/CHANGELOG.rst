*********
CHANGELOG
*********

.. contents:: :local:

1.6.1-alpha (inprogress)
========================

Likely the last update as "csvkitcat" before moving to csvmedkit

- csvwhere

- csvsed, csvrgrep
    - revamped required arguments and additional expressions

- csvsed

    + --like-grep now only filters by the first (required) expression, as chaining additional expressions likely results in a too-small result set for most use cases


- csvchart: killed, moved to csvviz library

1.5.6-alpha
===========

- changed various flags for many of the tools
- added ``--version`` flag
- cleaned up internals and csvkit inheritance
- [NOT YET FIXED] csvsed is fixed

1.5.5-alpha
===========

- :doc:`csvrgrep <moreutils/csvrgrep>`: like ``csvgrep``, but designed for when you want to concisely do a lot of regex filtering over a combination of columns

- csvsed: reworking its internals. Still being worked on, but current tests pass


1.5.1-alpha
===========

- the ``regex`` module seems to be very slow (e.g. csvsed), so it's been replaced with standard ``re`` in all tools except ``csvnorm``. Hopefully that's ok!


1.5.0-alpha
===========

:doc:`moreutils/csvgroupby`: for doing the equivalent of SQL ``GROUP BY [columns]``

1.4.0-alpha
===========

:doc:`csvpivot <moreutils/csvpivot>`: Pivot a table on rows and columns (TK better label)


1.3.7-alpha
===========

:doc:`csvflatten <moreutils/csvflatten>` tweaked:
- If a value contains newlines, then csvflatten will print newlines/rows; this is independent of whether the chop-length has been set.


1.3.5-alpha
===========

:doc:`csvcount <moreutils/csvcount>` has been overhauled:

- Basic functionality returns not just number of rows, but cells, empty rows+cells, and blank lines
- Restrict columns to search with``-c/--column``


1.3.0-alpha
============

* :doc:`csvxfind <moreutils/csvxfind>`: Findall regex matches in [COLUMN] and group concat them into a new column



1.2.0-alpha
===========

* :doc:`csvxcap <moreutils/csvxcap>`: Extract captured group patterns from one column and create new columns


1.1.0-alpha
===========

* :doc:`csvxplit <moreutils/csvxplit>`: create ``n`` new columns based on splitting a [COLUMN] by [PATTERN]

1.0.1-alpha
===========

* :doc:`csvnorm <moreutils/csvnorm>`: renamed and refactored from ``csvsqueeze``

    - csvnorm -C/--change-case for converting values to all upper or lower


1.0.0-alpha
===========

Basic functionality and testing for these tools:

* :doc:`csvcount <moreutils/csvcount>`
* :doc:`csvflatten <moreutils/csvflatten>`
* :doc:`csvsed <moreutils/csvflatten>`
* :doc:`csvslice <moreutils/csvslice>`
* csvsqueeze (likely to be refactored)



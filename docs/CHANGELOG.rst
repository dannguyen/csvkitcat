*********
CHANGELOG
*********

.. contents:: :local:


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



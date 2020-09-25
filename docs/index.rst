=========
csvkitcat
=========



.. toctree::
    :maxdepth: 1

    CHANGELOG



.. _the-utilities

Utilities
=========

.. toctree::
    :maxdepth: 1

    /moreutils/csvcount
    /moreutils/csvflatten
    /moreutils/csvgroupby
    /moreutils/csvnorm
    /moreutils/csvpivot
    /moreutils/csvrgrep
    /moreutils/csvsed
    /moreutils/csvslice
    /moreutils/csvxcap
    /moreutils/csvxfind
    /moreutils/csvxplit



FAQ
===

Q. How is this related to `wireservice/csvkit <https://github.com/wireservice/csvkit>`_?

A. **csvkitcat** is an extension of *csvkit* (and thus has csvkit and `agate <https://github.com/wireservice/agate>`_  as dependencies) that adds a bunch of new command-line utilities for data-wrangling convenience.


Q. What are the point of these new utilities?

A. As useful as core csvkit is, there are still a bunch of common data-wrangling tasks that are cumbersome to perform even when the data is in a spreadsheet or SQL database. "Cumbersome", in the sense that you'd basically have to write a custom Python script to do them.


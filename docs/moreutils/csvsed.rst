******
csvsed
******

.. contents:: :local:


Description
===========

Like ``sed``, but on a per-column basis




Examples
========


Basic example::

    $ csvsed -E '(?i)(?:Miss|Mrs|Ms)\.? *(.+)' 'The Ms. \1' examples/honorifics-fem.csv


    code,name
    1,Ms. Smith
    2,Ms. Daisy
    3,Ms. Doe
    4,Ms. Miller
    5.Ms. Lee
    6.Ms. maam





Cleaning up currency values TK FIX CODE FIRST

- remove commas and spaces
- replace negative notation, from ``(42)`` to ``-42``
- add a decimal amount for all whole dollar values

    $ csvsed -c 'revenue,gross' \
        -E '[$, ]' '' \
        -E '\((.+?)\)' '\-\1' \
        -E '(?<=\d)(\d{2})$' '\1.00' \
        examples/ledger.csv

    id,name,revenue,gross
    001,apples,21456.00,3210.45
    002,bananas,2442.00,-1234.00
    003,cherries,9700.55,-7.90
    004,dates,4102765.33,18765.00
    005,eggplants,3987.00,501.00
    006,figs,30333.00,-777.66
    006,grapes,154321.98,-32654.00

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

    $ csvsed '(?i)(?:Miss|Mrs|Ms)\.? *(.+)' 'The Ms. \1' examples/honorifics-fem.csv


    code,name
    1,Ms. Smith
    2,Ms. Daisy
    3,Ms. Doe
    4,Ms. Miller
    5.Ms. Lee
    6.Ms. maam



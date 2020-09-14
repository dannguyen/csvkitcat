********
csvslice
********

.. contents:: :local:



Description
===========

Returns the header, plus rows in the specified 0-index range, half-open-interval

Similar to `xsv slice <https://github.com/BurntSushi/xsv#available-commands>`_



Example::

    $ csvslice -B 2 -L 2 examples/yes.csv

    code,value
    3,Yes
    4,Y



Examples
========

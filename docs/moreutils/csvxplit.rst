********
csvxplit
********


.. contents:: :local:


Description
===========

Split a column by pattern into n-columns




Examples
========


Example with literal match::


    $ csvxplit -n 2 items '|' examples/pipes.csv

    code,items,items_xs_0,items_xs_1,items_xs_2
    0001,hey,hey,,
    0002,hello|world,hello,world,
    0003,a|b|c|d|,a,b,c|d|


With regex::

    $ csvxplit -n 2 items '\|' examples/pipes.csv

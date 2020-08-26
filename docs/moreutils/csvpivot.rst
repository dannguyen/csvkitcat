********
csvpivot
********

.. contents:: :local:


Description
===========

Do a simple pivot table, by row, column, or row and column



Examples
========


Basic counting
--------------

Pivot by row::

    $ csvpivot -r race examples/peeps.csv

    race,Count
    white,1
    asian,2
    black,2
    latino,1


Pivot by column::


    female,male
    4,2

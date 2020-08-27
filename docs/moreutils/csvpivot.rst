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

Pivot by rows::

    $ csvpivot -r race examples/peeps.csv

    race,Count
    white,1
    asian,2
    black,2
    latino,1

Pivot across several fields (TK?) of rows::

    $ csvpivot -r race,gender examples/peeps.csv

    race,gender,Count
    white,female,1
    asian,male,1
    asian,female,1
    black,female,2
    latino,male,1

Pivot along columns::

    $ csvpivot -c gender examples/peeps.csv

    female,male
    4,2


Pivot on rows and columns::

    $ csvpivot -r race -c gender examples/peeps.csv

    race,female,male
    white,1,0
    asian,1,1
    black,2,0
    latino,0,1

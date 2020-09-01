********
csvgroupby
********

.. contents:: :local:


Description
===========

Do SQL-like ``GROUP BY`` aggregations

Similar to :any:`moreutils/csvpivot`, except ``csvgroupby`` allows for multiple aggregation value columns.


Example::

    $ csvgroupby -c 'gender,race' -a count -a mean:age  examples/peeps.csv

    gender,race,Count,Mean_of_age
    female,white,1,20
    female,black,2,22.5
    female,asian,1,25
    male,asian,1,20
    male,latino,1,25

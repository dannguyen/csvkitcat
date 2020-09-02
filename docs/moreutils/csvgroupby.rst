**********
csvgroupby
**********

.. contents:: :local:


Description
===========

Do SQL-like ``GROUP BY`` aggregations

Similar to :any:`/moreutils/csvpivot`, except ``csvgroupby`` allows for multiple aggregation value columns. Call ``-a/--agg`` multiple times for multiple aggregations.


Example::

    $ csvgroupby -c 'gender,race' -a count -a mean:age -a 'TOTAL age|sum:age' examples/peeps.csv | csvlook

    | gender | race   | Count | Mean_of_age | TOTAL age |
    | ------ | ------ | ----- | ----------- | --------- |
    | female | white  |     1 |        20.0 |        20 |
    | female | black  |     2 |        22.5 |        45 |
    | female | asian  |     1 |        25.0 |        25 |
    | male   | asian  |     1 |        20.0 |        20 |
    | male   | latino |     1 |        25.0 |        25 |




********
csvcount
********

.. contents:: :local:


Description
===========

Count the number of rows, cells, empty rows and cells, and blank lines

Optionally, given a regex or list of regexes, count:

- the number of rows with at least 1 match
- the number of cells with at least 1 match
- the number of total matches (e.g. some cell values may match the patterns more than once)


Examples
========


Basic counting of file records
------------------------------

Basic example::

    $ csvcount examples/dummy4.csv

    rows,cells,empty_rows,empty_cells,blank_lines
    4,12,0,0,0


On real world data::

    $ csvcount examples/realdata/osha-violation.csv |  csvlook -I

    | rows  | cells  | empty_rows | empty_cells | blank_lines |
    | ----- | ------ | ---------- | ----------- | ----------- |
    | 29999 | 299990 | 0          | 39035       | 0           |



On file with empty rows and cells::

    $ csvcount examples/empties.csv

    rows,cells,empty_rows,empty_cells,blank_lines
    4,12,1,4,0


On file with blank lines::

    $  csvcount examples/blankedlines.csv

    rows,cells,empty_rows,empty_cells,blank_lines
    3,9,0,0,4



Counting of patterns
--------------------


Counting words with at least 5 letters::


    $ csvcount -P '[A-z]{5,}' examples/longvals.csv | csvlook

    | pattern   | rows | cells | matches |
    | --------- | ---- | ----- | ------- |
    | [A-z]{5,} |    3 |     9 |      43 |


Limiting the match searching to the ``description`` column::

    $ csvcount -P '[A-z]{5,}' -c description examples/longvals.csv | csvlook

    | pattern   | rows | cells | matches |
    | --------- | ---- | ----- | ------- |
    | [A-z]{5,} |    3 |     3 |      31 |


Counting (naively) the number of @mentions, #hastags, and URLs in tweet texts::


    $ csvcount -P '@\w+' -P '#\w+' -P 'https:' \
        -c text examples/realdata/tweets-whitehouse.csv \
        | csvlook


    | pattern |  rows | cells | matches |
    | ------- | ----- | ----- | ------- |
    | @\w+    | 1,591 | 1,591 |   2,266 |
    | #\w+    |   409 |   409 |     560 |
    | https:  | 2,596 | 2,596 |   2,938 |

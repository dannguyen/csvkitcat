********
csvrgrep
********

.. contents:: :local:


Description
===========

Basically like ``csvgrep``, but designed for situations in which you want to do a variety of filters across a variety of column combinations.

Example::

    $ csvrgrep -E '\w{5,}' 'name,address' \
               -E '\d{3}-\d{4}-XX'  \
               -E 'open\w*|close\w*' 'status,revised_status' \
               examples/SOMERANDODATA.csv


Examples
========


To mimic csvkit default behavior::


    $ csvrgrep -c 1,2,3 -E 'pattern' --match-literal --all-match data.csv

By default, ``csvrgrep`` returns matches when any column matches the regex pattern

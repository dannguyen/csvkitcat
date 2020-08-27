********
csvchart
********

.. contents:: :local:


Description
===========

Create a chart from the command-line! WHEEEE


Example
-------

::

    $ csvchart examples/tings.csv

    name   things
    Alice      20 ▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
    Bob        10 ▓░░░░░░░░░░░░░░░░░░░░░░
    Carson     30 ▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
                  +---------------+---------------+----------------+---------------+
                  0.0            7.5            15.0             22.5           30.0

Wrangling examples
==================

Make a bar chart of the 10 most frequently occurring crime incidents::


    $ csvpivot -r 'Primary Type' examples/realdata/chicago-crime.csv \
        | csvsort -c Count -r \
        | csvslice --len 10 \
        | csvchart


    Primary Type        Count
    BATTERY               217 ▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
    THEFT                 188 ▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
    CRIMINAL DAMAGE       142 ▓░░░░░░░░░░░░░░░░░░░░░░░░░
    ASSAULT                81 ▓░░░░░░░░░░░░░░
    OTHER OFFENSE          60 ▓░░░░░░░░░░░
    DECEPTIVE PRACTICE     58 ▓░░░░░░░░░░
    MOTOR VEHICLE THEFT    51 ▓░░░░░░░░░
    BURGLARY               50 ▓░░░░░░░░░
    WEAPONS VIOLATION      41 ▓░░░░░░░
    NARCOTICS              35 ▓░░░░░░
                              +------------+------------+-------------+------------+
                              0           75           150           225         300

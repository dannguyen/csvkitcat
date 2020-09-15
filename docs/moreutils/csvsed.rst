******
csvsed
******

.. contents:: :local:


Description
===========

Like ``sed``, but on a per-column basis


Example::

    $ csvsed "Ab[bi].+" "Abby" -E "(B|R)ob.*" "\1ob" -E "(?:Jack|John).*" "John"  examples/aliases.csv


    id,to,from
    1,Abby,Bob
    2,Bob,John
    3,Abby,John
    4,John,Abner
    5,Rob,John
    6,Jon,Abby
    7,Rob,Abby



Examples
========


.. Basic example::

..     $ csvsed -E '(?i)(?:Miss|Mrs|Ms)\.? *(.+)' 'The Ms. \1' examples/honorifics-fem.csv


..     code,name
..     1,Ms. Smith
..     2,Ms. Daisy
..     3,Ms. Doe
..     4,Ms. Miller
..     5.Ms. Lee
..     6.Ms. maam



Multiple expressions
--------------------


Cleaning up currency values
^^^^^^^^^^^^^^^^^^^^^^^^^^^

- remove commas and spaces
- replace negative notation, from ``(42)`` to ``-42``
- add a decimal amount for all whole dollar values

.. code-block:: sh

    $ csvsed '[$, ]' "" examples/ledger.csv \
            -c 'revenue,gross' \
            -E '\((.+?)\)' '\-\1' \
            -E '(?<=\d)(\d{2})$' '\1.00'


::

    id,name,revenue,gross
    001,apples,21456.00,3210.45
    002,bananas,2442.00,-1234.00
    003,cherries,9700.55,-7.90
    004,dates,4102765.33,18765.00
    005,eggplants,3987.00,501.00
    006,figs,30333.00,-777.66
    006,grapes,154321.98,-32654.00


Replace entire field with ``-R/--replace``
------------------------------------------



.. code-block:: sh

    $ cat examples/rolodex.csv |
        csvsed -c phone '(?P<area>\d{3}).*?(?P<x>\d{3}).*?(?P<y>\d{4})' \
                        '(\g<area>)-\g<x>-\g<y>'


Output::

    name,zipcode,phone
    Andie,10003,((555)-123-4567
    Betty,23456,1-(800)-777-2222
    Caren,33033,1((900)-333-1212
    Denny,42742,(212)-867-5309
    Ellie,90210,(555)-404-2020


Some of the phone numbers have superfluous characters, like country calling code (i.e. "1-") and unneeded parentheses. Use the ``-R`` option to specify that the *replacement* pattern should overwrite the entire field:


.. code-block:: sh

    $ cat examples/rolodex.csv |
        csvsed -R -c phone '(?P<area>\d{3}).*?(?P<x>\d{3}).*?(?P<y>\d{4})' \
                        '(\g<area>)-\g<x>-\g<y>'


    name,zipcode,phone
    Andie,10003,(555)-123-4567
    Betty,23456,(800)-777-2222
    Caren,33033,(900)-333-1212
    Denny,42742,(212)-867-5309
    Ellie,90210,(555)-404-2020




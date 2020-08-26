**********
csvflatten
**********

.. contents:: :local:


Description
===========

Print records in column-per-line format. Best used in conjunction with `csvlook <https://csvkit.readthedocs.io/en/latest/scripts/csvlook.html>`_

Similar in concept to `xsv flatten <https://github.com/BurntSushi/xsv#available-commands>`_, though the output is much different.

TK/TODO: copy text/rationale from `original Github issue <https://github.com/dannguyen/csvkit/issues/1>`_



Basic example and transformation
================================

Given the file at :file:`examples/statecodes.csv`, which looks like this:

.. csv-table::
   :file: ../../examples/statecodes.csv
   :header-rows: 1


And then passing it into :command:`csvflatten`::

    $ csvflatten examples/statecodes.csv


Results in this output::

    fieldname,value
    code,IA
    name,Iowa
    ~~~~~~~~~,
    code,RI
    name,Rhode Island
    ~~~~~~~~~,
    code,TN
    name,Tennessee


Which looks like this as a table:

.. csv-table::
   :header-rows: 1

   fieldname,value
   code,IA
   name,Iowa
   ~~~~~~~~~,""
   code,RI
   name,Rhode Island
   ~~~~~~~~~,""
   code,TN
   name,Tennessee





More examples
=============


Shakespeare and csvlook::

    $ csvflatten examples/hamlet.csv | csvlook

    | fieldname | value                                          |
    | --------- | ---------------------------------------------- |
    | act       | 1                                              |
    | scene     | 5                                              |
    | speaker   | Horatio                                        |
    | lines     | Propose the oath, my lord.                     |
    | ~~~~~~~~~ |                                                |
    | act       | 1                                              |
    | scene     | 5                                              |
    | speaker   | Hamlet                                         |
    | lines     | Never to speak of this that you have seen,     |
    |           | Swear by my sword.                             |
    | ~~~~~~~~~ |                                                |
    | act       | 1                                              |
    | scene     | 5                                              |
    | speaker   | Ghost                                          |
    | lines     | [Beneath] Swear.                               |
    | ~~~~~~~~~ |                                                |
    | act       | 3                                              |
    | scene     | 4                                              |
    | speaker   | Gertrude                                       |
    | lines     | O, speak to me no more;                        |
    |           | These words, like daggers, enter in mine ears; |
    |           | No more, sweet Hamlet!                         |
    | ~~~~~~~~~ |                                                |
    | act       | 4                                              |
    | scene     | 7                                              |
    | speaker   | Laertes                                        |
    | lines     | Know you the hand?                             |


Chopping the text length to no more than 20 characters per line:

    $ csvflatten -X 20 examples/hamlet.csv | csvlook

    | fieldname | value                |
    | --------- | -------------------- |
    | act       | 1                    |
    | scene     | 5                    |
    | speaker   | Horatio              |
    | lines     | Propose the oath, my |
    |           |  lord.               |
    | ~~~~~~~~~ |                      |
    | act       | 1                    |
    | scene     | 5                    |
    | speaker   | Hamlet               |
    | lines     | Never to speak of th |
    |           | is that you have see |
    |           | n,                   |
    |           | Swear by my sword.   |
    | ~~~~~~~~~ |                      |
    | act       | 1                    |
    | scene     | 5                    |
    | speaker   | Ghost                |
    | lines     | [Beneath] Swear.     |
    | ~~~~~~~~~ |                      |
    | act       | 3                    |
    | scene     | 4                    |
    | speaker   | Gertrude             |
    | lines     | O, speak to me no mo |
    |           | re;                  |
    |           | These words, like da |
    |           | ggers, enter in mine |
    |           |  ears;               |
    |           | No more, sweet Hamle |
    |           | t!                   |
    | ~~~~~~~~~ |                      |
    | act       | 4                    |
    | scene     | 7                    |
    | speaker   | Laertes              |
    | lines     | Know you the hand?   |




Another example with csvlook::

    $ csvflatten examples/longvals.csv -X 50 | csvlook | pbcopy


::

    | fieldname    | value                                              |
    | ------------ | -------------------------------------------------- |
    | title        | Raising Arizona                                    |
    | release_date | March 13, 1987                                     |
    | length       | 94                                                 |
    | box_office   | 292000000                                          |
    | description  | Repeat convict "Hi" and police officer "Ed" meet i |
    |              | n prison, get married, and hope to raise a family. |
    | url          | https://en.wikipedia.org/wiki/Raising_Arizona      |
    | ~~~~~~~~~    |                                                    |
    | title        | Face/Off                                           |
    | release_date | June 27, 1997                                      |
    | length       | 139                                                |
    | box_office   | 80000000                                           |
    | description  | John Travolta plays an FBI agent and Nicolas Cage  |
    |              | plays a terrorist, sworn enemies who assume each o |
    |              | ther's physical appearance.                        |
    | url          | https://en.wikipedia.org/wiki/Face/Off             |
    | ~~~~~~~~~    |                                                    |
    | title        | Adaptation                                         |
    | release_date | Dec. 6, 2002                                       |
    | length       | 114                                                |
    | box_office   | 32800000                                           |
    | description  | The self-loathing Charlie Kaufman is hired to writ |
    |              | e the screenplay adaptation of Susan Orlean's The  |
    |              | Orchid Thief.                                      |
    | url          | https://en.wikipedia.org/wiki/Adaptation_(film)    |


Giving each chopped field a header::


    $ csvflatten examples/longvals.csv -X 50 --chop-labels | csvlook


    | fieldname     | value                                              |
    | ------------- | -------------------------------------------------- |
    | title         | Raising Arizona                                    |
    | release_date  | March 13, 1987                                     |
    | length        | 94                                                 |
    | box_office    | 292000000                                          |
    | description   | Repeat convict "Hi" and police officer "Ed" meet i |
    | description~1 | n prison, get married, and hope to raise a family. |
    | url           | https://en.wikipedia.org/wiki/Raising_Arizona      |
    | ~~~~~~~~~     |                                                    |
    | title         | Face/Off                                           |
    | release_date  | June 27, 1997                                      |
    | length        | 139                                                |
    | box_office    | 80000000                                           |
    | description   | John Travolta plays an FBI agent and Nicolas Cage  |
    | description~1 | plays a terrorist, sworn enemies who assume each o |
    | description~2 | ther's physical appearance.                        |
    | url           | https://en.wikipedia.org/wiki/Face/Off             |
    | ~~~~~~~~~     |                                                    |
    | title         | Adaptation                                         |
    | release_date  | Dec. 6, 2002                                       |
    | length        | 114                                                |
    | box_office    | 32800000                                           |
    | description   | The self-loathing Charlie Kaufman is hired to writ |
    | description~1 | e the screenplay adaptation of Susan Orlean's The  |
    | description~2 | Orchid Thief.                                      |
    | url           | https://en.wikipedia.org/wiki/Adaptation_(film)    |

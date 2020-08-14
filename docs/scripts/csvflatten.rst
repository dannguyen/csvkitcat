**********
csvflatten
**********


Description
===========

Flattens lorem TK



Examples
========



Basic use-case with csvlook::

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


Labeling the chopped up values::


    $ csvflatten examples/longvals.csv -X 50 --chop-labels | csvlook

********
csvxfind
********


.. contents:: :local:


Description
===========

Find all regex [PATTERN] in [COLUMN], create new column with all matches



Examples
========

Basic::


    $ csvxfind 'text' '@\w+' examples/mentions.csv | csvlook


    | id | text                                                 | text_xfind              |
    | -- | ---------------------------------------------------- | ----------------------- |
    |  1 | hey                                                  |                         |
    |  2 | hello @world                                         | @world                  |
    |  3 | Just like @a_prayer, your @Voice can take me @there! | @a_prayer;@Voice;@there |



Specify delimiter with ``-D``::

    $ csvxfind -D ', '  'text' '@\w+' examples/mentions.csv | csvlook

    | id | text                                                 | text_xfind                |
    | -- | ---------------------------------------------------- | ------------------------- |
    |  1 | hey                                                  |                           |
    |  2 | hello @world                                         | @world                    |
    |  3 | Just like @a_prayer, your @Voice can take me @there! | @a_prayer, @Voice, @there |


Limit matches with ``-n``::

    $ csvxfind -n 2 'text' '@\w+' examples/mentions.csv | csvlook

    | id | text                                                 | text_xfind       |
    | -- | ---------------------------------------------------- | ---------------- |
    |  1 | hey                                                  |                  |
    |  2 | hello @world                                         | @world           |
    |  3 | Just like @a_prayer, your @Voice can take me @there! | @a_prayer;@Voice |

*******
csvxcap
*******


.. contents:: :local:


Description
===========

Extract captured group patterns from one column and create new columns




Examples
========


Example with no captured group, just a pattern::


    $ csvxcap 'name' '\w+' examples/honorifics-fem.csv | csvlook

    | code | name       | name_xcap |
    | ---- | ---------- | --------- |
    |    1 | Mrs. Smith | Mrs       |
    |    2 | Miss Daisy | Miss      |
    |    3 | Ms. Doe    | Ms        |
    |    4 | Mrs Miller | Mrs       |
    |    5 | Ms Lee     | Ms        |
    |    6 | miss maam  | miss      |



Example with captured groups::


    $ csvxcap 'name' '(\w+)\.? (\w+)' examples/honorifics-fem.csv | csvlook

    | code | name       | name_xcap1 | name_xcap2 |
    | ---- | ---------- | ---------- | ---------- |
    |    1 | Mrs. Smith | Mrs        | Smith      |
    |    2 | Miss Daisy | Miss       | Daisy      |
    |    3 | Ms. Doe    | Ms         | Doe        |
    |    4 | Mrs Miller | Mrs        | Miller     |
    |    5 | Ms Lee     | Ms         | Lee        |
    |    6 | miss maam  | miss       | maam       |





Example with named captured groups (allows naming of headers)::


    $ csvxcap 'name' '(?P<prefix>\w+)\.? (?P<sur>\w+)' examples/honorifics-fem.csv | csvlook


    | code | name       | name_prefix | name_sur |
    | ---- | ---------- | ----------- | -------- |
    |    1 | Mrs. Smith | Mrs         | Smith    |
    |    2 | Miss Daisy | Miss        | Daisy    |
    |    3 | Ms. Doe    | Ms          | Doe      |
    |    4 | Mrs Miller | Mrs         | Miller   |
    |    5 | Ms Lee     | Ms          | Lee      |
    |    6 | miss maam  | miss        | maam     |

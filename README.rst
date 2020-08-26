*********
csvkitcat
*********


csvkitcat is a library that supplements (and depends on) the great `wireservice/csvkit <https://github.com/wireservice/csvkit>`_. It exists because csvkit is no longer adding new tools to its core functionality.




New tools and utilities:

- csvcount: just count records
- csvflatten: transpose records in a format easier to view in text files
- csvnorm: normalize whitespace/newlines and character casing
- csvsed: like ``sed``, but done at the columnar level
- csvslice: like ``xsv slice``
- csvxplit: split a given column by a pattern into n new columns


See more docs at `Read The Docs <https://csvkitcat.readthedocs.io/>`_



See `CHANGELOG <docs/CHANGELOG.rst>`_


CSVKit documentation
====================


csvkit is a suite of command-line tools for converting to and working with CSV, the king of tabular file formats.

It is inspired by pdftk, GDAL and the original csvcut tool by Joe Germuska and Aaron Bycoffe.

Important links:

* Documentation: http://csvkit.rtfd.org/
* Repository:    https://github.com/wireservice/csvkit
* Issues:        https://github.com/wireservice/csvkit/issues
* Schemas:       https://github.com/wireservice/ffs


Dev notes
=========

How to publish: https://realpython.com/pypi-publish-python-package/

.. code-block:: shell

    python setup.py sdist bdist_wheel
    twine upload dist/*

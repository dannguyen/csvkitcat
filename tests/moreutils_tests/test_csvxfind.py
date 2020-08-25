#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import six

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from csvkit.exceptions import ColumnIdentifierError

from csvkitcat.exceptions import ArgumentErrorTK
from csvkitcat.moreutils.csvxfind import CSVXfind, launch_new_instance
from tests.utils import CSVKitTestCase, stdin_as_string
from unittest import skip as skiptest


class TestCSVXfind(CSVKitTestCase):
    Utility = CSVXfind
    default_args = ["a", "|"]

    def test_launch_new_instance(self):
        with patch.object(
            sys,
            "argv",
            [self.Utility.__name__.lower(), *self.default_args, "examples/dummy.csv"],
        ):
            launch_new_instance()

    def test_basic_dummy_match(self):
        """
        creates 1 xfind col
        """
        self.assertLines(
            ["a", r"\d", "examples/dummy.csv"], ["a,b,c,a_xfind", "1,2,3,1",]
        )

    def test_basic_dummy_no_match(self):
        """
        creates 1 xfind col even when there's no match
        """
        self.assertLines(["a", ";", "examples/dummy.csv"], ["a,b,c,a_xfind", "1,2,3,",])

    def test_basic_mentions(self):
        self.assertLines(
            ["text", r"@\w+", "examples/mentions.csv"],
            [
                "id,text,text_xfind",
                "1,hey,",
                "2,hello @world,@world",
                '3,"Just like @a_prayer, your @Voice can take me @there!",@a_prayer;@Voice;@there',
            ],
        )

    def test_basic_mentions_specify_delimiter(self):
        self.assertLines(
            ["-D", ", ", "text", r"@\w+", "examples/mentions.csv"],
            [
                "id,text,text_xfind",
                "1,hey,",
                "2,hello @world,@world",
                '3,"Just like @a_prayer, your @Voice can take me @there!","@a_prayer, @Voice, @there"',
            ],
        )

    def test_basic_mentions_limit_matches(self):
        self.assertLines(
            ["-n", "2", "text", r"@\w+", "examples/mentions.csv"],
            [
                "id,text,text_xfind",
                "1,hey,",
                "2,hello @world,@world",
                '3,"Just like @a_prayer, your @Voice can take me @there!",@a_prayer;@Voice',
            ],
        )

    ### error stuff

    def test_error_when_invalid_column_given_as_argument(self):
        with self.assertRaises(ColumnIdentifierError) as c:
            self.get_output(["WTF", ";", "examples/dummy.csv"])

    def test_error_when_multiple_columns_given_as_argument(self):
        with self.assertRaises(ArgumentErrorTK) as c:
            self.get_output(["a,b,c", ";", "examples/dummy.csv"])
        assert "argument expects exactly one column identifier" in str(c.exception)

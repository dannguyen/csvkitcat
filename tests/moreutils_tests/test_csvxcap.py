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
from csvkitcat.moreutils.csvxcap import CSVXcap, launch_new_instance
from tests.utils import CSVKitTestCase, stdin_as_string
from unittest import skip as skiptest


class TestCSVXcap(CSVKitTestCase):
    Utility = CSVXcap
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
        creates 1 xcap col
        """
        self.assertLines(
            ["a", r"\d", "examples/dummy.csv"], ["a,b,c,a_xcap", "1,2,3,1",]
        )

    def test_basic_dummy_no_match(self):
        """
        creates 1 xcap col even when there's no match
        """
        self.assertLines(["a", ";", "examples/dummy.csv"], ["a,b,c,a_xcap", "1,2,3,",])

    def test_no_cap_group(self):
        self.assertLines(
            ["name", r"[A-Z]\w+", "examples/honorifics-fem.csv"],
            [
                "code,name,name_xcap",
                "1,Mrs. Smith,Mrs",
                "2,Miss Daisy,Miss",
                "3,Ms. Doe,Ms",
                "4,Mrs Miller,Mrs",
                "5,Ms Lee,Ms",
                "6,miss maam,",
            ],
        )

    def test_numbered_cap_groups(self):
        self.assertLines(
            ["name", r"([A-Z]\w+)\. (\w+)", "examples/honorifics-fem.csv"],
            [
                "code,name,name_xcap1,name_xcap2",
                "1,Mrs. Smith,Mrs,Smith",
                "2,Miss Daisy,,",
                "3,Ms. Doe,Ms,Doe",
                "4,Mrs Miller,,",
                "5,Ms Lee,,",
                "6,miss maam,,",
            ],
        )

    def test_named_cap_groups(self):
        self.assertLines(
            [
                "name",
                r"(?P<honor>[A-Z]\w+)\. (?P<surname>\w+)",
                "examples/honorifics-fem.csv",
            ],
            [
                "code,name,name_honor,name_surname",
                "1,Mrs. Smith,Mrs,Smith",
                "2,Miss Daisy,,",
                "3,Ms. Doe,Ms,Doe",
                "4,Mrs Miller,,",
                "5,Ms Lee,,",
                "6,miss maam,,",
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

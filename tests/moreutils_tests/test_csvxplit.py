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
from csvkitcat.moreutils.csvxplit import CSVXplit, launch_new_instance
from tests.utils import CSVKitTestCase, stdin_as_string
from unittest import skip as skiptest


class TestCSVXplit(CSVKitTestCase):
    Utility = CSVXplit
    default_args = ["a", "|"]

    def test_launch_new_instance(self):
        with patch.object(
            sys,
            "argv",
            [self.Utility.__name__.lower(), *self.default_args, "examples/dummy.csv"],
        ):
            launch_new_instance()

    def test_basic_dummy(self):
        """
        creates 2 split cols even when there's no match
        """
        self.assertLines(
            ["2", ";", "examples/dummy.csv"], ["a,b,c,b_xp0,b_xp1", "1,2,3,2,",]
        )

    def test_basic_pipes_no_match(self):
        self.assertLines(
            ["-n", "2", "items", "@", "examples/pipes.csv"],
            [
                "code,items,items_xp0,items_xp1,items_xp2",
                "0001,hey,hey,,",
                "0002,hello|world,hello|world,,",
                "0003,a|b|c|d|,a|b|c|d|,,",
            ],
        )

    def test_basic_pipes_match(self):
        self.assertLines(
            ["items", "|", "examples/pipes.csv"],
            [
                "code,items,items_xp0,items_xp1",
                "0001,hey,hey,",
                "0002,hello|world,hello,world",
                "0003,a|b|c|d|,a,b|c|d|",
            ],
        )

    def test_basic_pipes_match_n_cols_set(self):
        self.assertLines(
            ["-n", "3", "items", "|", "examples/pipes.csv"],
            [
                "code,items,items_xp0,items_xp1,items_xp2,items_xp3",
                "0001,hey,hey,,,",
                "0002,hello|world,hello,world,,",
                "0003,a|b|c|d|,a,b,c,d|",
            ],
        )

    def test_regex_pipes(self):
        """
        when splitting by regex pipe, the behavior from regex module is that newvals[0] is an empty string :shrug:
        """
        self.assertLines(
            ["-r", "items", "|", "examples/pipes.csv"],
            [
                "code,items,items_xp0,items_xp1",
                "0001,hey,,hey",
                "0002,hello|world,,hello|world",
                "0003,a|b|c|d|,,a|b|c|d|",
            ],
        )

    ### error stuff
    def test_error_when_n_split_count_is_less_than_1(self):
        with self.assertRaises(ArgumentErrorTK) as c:
            self.get_output(["-n", "0", "a", ";", "examples/dummy.csv"])
        assert "must be greater or equal to 1, not: 0" in str(c.exception)

    def test_error_when_invalid_column_given_as_argument(self):
        with self.assertRaises(ColumnIdentifierError) as c:
            self.get_output(["d", ";", "examples/dummy.csv"])

    def test_error_when_multiple_columns_given_as_argument(self):
        with self.assertRaises(ArgumentErrorTK) as c:
            self.get_output(["a,b,c", ";", "examples/dummy.csv"])
        assert "argument expects exactly one column identifier" in str(c.exception)

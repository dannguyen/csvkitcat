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
from csvkitcat.moreutils.csvslice import CSVSlice, launch_new_instance
from tests.utils import CSVKitTestCase, stdin_as_string, EmptyFileTests
from unittest import skip as skiptest


class TestCSVSlice(CSVKitTestCase, EmptyFileTests):
    Utility = CSVSlice
    default_args = ["-S", "1"]

    def test_launch_new_instance(self):
        with patch.object(
            sys,
            "argv",
            [self.Utility.__name__.lower()]
            + self.default_args
            + ["examples/dummy.csv"],
        ):
            launch_new_instance()

    def test_basic_start(self):
        """
        a,b,c
        1,2,3
        4,5,6
        7,8,9
        10,11,12
        """
        self.assertLines(
            ["-S", "2", "examples/dummy4.csv"], ["a,b,c", "7,8,9", "10,11,12",]
        )

    def test_start_negative_end(self):
        """basically like tail

        TODO: wait is it really?
        """

        self.assertLines(
            ["-S", "-2", "examples/dummy4.csv"], ["a,b,c", "7,8,9", "10,11,12",]
        )

    def test_basic_end(self):
        """
        remember it is and_half_open_interval
        """
        self.assertLines(
            ["-E", "2", "examples/dummy4.csv"], ["a,b,c", "1,2,3", "4,5,6",]
        )

    def test_basic_start_and_end(self):
        self.assertLines(
            ["-E", "3", "-S", "1", "examples/dummy4.csv"], ["a,b,c", "4,5,6", "7,8,9",]
        )

    def test_basic_negative_end(self):
        self.assertLines(["-E", "-3", "examples/dummy4.csv"], ["a,b,c", "1,2,3",])

    def test_negative_start_and_end(self):
        self.assertLines(
            ["-S", "-3", "-E", "-2", "examples/dummy4.csv"], ["a,b,c", "4,5,6",]
        )

    def test_basic_length(self):
        self.assertLines(
            ["-L", "2", "examples/dummy4.csv"], ["a,b,c", "1,2,3", "4,5,6",]
        )

    def test_basic_length_and_start(self):
        self.assertLines(
            ["-S", "1", "-L", "2", "examples/dummy4.csv"], ["a,b,c", "4,5,6", "7,8,9",]
        )

    ### index option
    def test_basic_index(self):
        self.assertLines(["-i", "0", "examples/dummy4.csv"], ["a,b,c", "1,2,3",])

        self.assertLines(["-i", "-2", "examples/dummy4.csv"], ["a,b,c", "7,8,9",])

    def test_index_is_equivalent_to_start_and_length_opts(self):
        idx_rows = self.get_output_as_list(["--index", "2", "examples/dummy4.csv"])
        slen_rows = self.get_output_as_list(
            ["--start", "2", "--len", "1", "examples/dummy4.csv"]
        )

        for i, idx_row in enumerate(idx_rows):
            self.assertEqual(idx_row, slen_rows[i])

    #### error stuff
    def test_error_when_both_length_and_end_provided(self):
        with self.assertRaises(ArgumentErrorTK) as context:
            u = self.get_output(["-E", "3", "-L", "2", "examples/dummy4.csv"])
        assert "Cannot set both" in str(context.exception)

    def test_error_when_no_slice_options(self):
        with self.assertRaises(ArgumentErrorTK) as context:
            u = self.get_output(["examples/dummy4.csv"])
        assert "At least 1 of" in str(context.exception)

    def test_error_when_index_and_other_slice_options_are_set(self):
        with self.assertRaises(ArgumentErrorTK) as c1:
            self.get_output(["-i", "1", "-S", "1", "examples/dummy4.csv"])

        with self.assertRaises(ArgumentErrorTK) as c2:
            self.get_output(["-i", "1", "-E", "2", "examples/dummy4.csv"])

        with self.assertRaises(ArgumentErrorTK) as c3:
            self.get_output(["-i", "1", "-L", "1", "examples/dummy4.csv"])

        assert "Slice index cannot be set if start/end/length are also defined" in str(
            c3.exception
        )


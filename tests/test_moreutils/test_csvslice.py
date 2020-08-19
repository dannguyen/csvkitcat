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
from csvkitcat.moreutils.csvslice import CSVSlice,  launch_new_instance
from tests.utils import CSVKitTestCase, stdin_as_string, EmptyFileTests
from unittest import skip as skiptest

class TestCSVSlice(CSVKitTestCase, EmptyFileTests):
    Utility = CSVSlice


    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', [self.Utility.__name__.lower(), 'examples/dummy.csv']):
            launch_new_instance()



    def test_basic_start(self):
        """
        a,b,c
        1,2,3
        4,5,6
        7,8,9
        10,11,12
        """
        self.assertLines(['-S', '2', 'examples/dummy4.csv' ], [
            "a,b,c",
            "7,8,9",
            "10,11,12",
        ])


    def test_start_negative_end(self):
        """basically like tail"""
        self.assertLines(['-S', '-2', 'examples/dummy4.csv' ], [
            "a,b,c",
            "7,8,9",
            "10,11,12",
        ])


    def test_basic_end(self):
        """
        remember it is and_half_open_interval
        """
        self.assertLines(['-E', '2', 'examples/dummy4.csv' ], [
            "a,b,c",
            "1,2,3",
            "4,5,6",
        ])


    def test_basic_start_and_end(self):
        self.assertLines(['-E', '3', '-S', '1',
                            'examples/dummy4.csv' ], [
            "a,b,c",
            "4,5,6",
            '7,8,9',
        ])


    def test_basic_negative_end(self):
        self.assertLines(['-E', '-3',
                            'examples/dummy4.csv' ], [
            "a,b,c",
            "1,2,3",
        ])


    def test_negative_start_and_end(self):
        self.assertLines(['-S', '-3', '-E', '-2',
                            'examples/dummy4.csv' ], [
            "a,b,c",
            "4,5,6",
        ])



    def test_basic_length(self):
        self.assertLines(['-L', '2', 'examples/dummy4.csv' ], [
            "a,b,c",
            "1,2,3",
            "4,5,6",
        ])

    def test_basic_length_and_start(self):
        self.assertLines([ '-S', '1', '-L', '2', 'examples/dummy4.csv' ], [
            "a,b,c",
            "4,5,6",
            "7,8,9",
        ])



    ### index option
    @skiptest("Temporarily not implemented")
    def test_basic_index(self):
        """
        a,b,c
        1,2,3
        4,5,6
        7,8,9
        10,11,12
        """
        self.assertLines(['-i', '0', 'examples/dummy4.csv' ], [
            "a,b,c",
            "1,2,3",
        ])

        self.assertLines(['-i', '-2', 'examples/dummy4.csv' ], [
            "a,b,c",
            "7,8,9",
        ])



    #### error stuff
    def test_error_when_both_length_and_end_provided(self):
        with self.assertRaises(ArgumentErrorTK):
            u = self.get_output([ '-E', '3', '-L', '2', 'examples/dummy4.csv' ])


    @skiptest("Temporarily not implemented")
    def test_error_when_index_and_start_end_or_len(self):
        pass

    @skiptest("OBSOLETE")
    def test_error_when_start_bigger_than_end(self):
        with self.assertRaises(ArgumentErrorTK):
            u = self.get_output([ '-S', '3', '-E', '1', 'examples/dummy4.csv' ])

    @skiptest("OBSOLETE")
    def test_error_when_start_equal_to_end(self):
        with self.assertRaises(ArgumentErrorTK):
            u = self.get_output([ '-S', '1', '-E', '1', 'examples/dummy4.csv' ])


"""
to write:

test_index
"""

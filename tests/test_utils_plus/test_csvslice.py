#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import six

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from csvkit.exceptions import ColumnIdentifierError
from csvkitcat.utils_plus.csvslice import CSVSlice,  launch_new_instance
from tests.utils import CSVKitTestCase, stdin_as_string, EmptyFileTests

import unittest
from unittest import skip as skiptest

@skiptest("Temporarily not implemented")
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
        self.assertLines(['--is', '2', 'examples/dummy4.csv' ], [
            "a,b,c",
            "7,8,9",
            "10,11,12",
        ])


    def test_basic_end(self):
        """
        a,b,c
        1,2,3
        4,5,6
        7,8,9
        10,11,12
        """
        self.assertLines(['--ie', '2', 'examples/dummy4.csv' ], [
            "a,b,c",
            "1,2,3",
            "4,5,6",
            "7,8,9",
        ])


    def test_basic_length(self):
        """
        a,b,c
        1,2,3
        4,5,6
        7,8,9
        10,11,12
        """
        self.assertLines(['--il', '2', 'examples/dummy4.csv' ], [
            "a,b,c",
            "1,2,3",
            "4,5,6",
        ])




"""
to write:

test_index
"""

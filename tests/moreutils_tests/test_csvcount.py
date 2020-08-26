#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import six

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from tests.utils import CSVKitTestCase, stdin_as_string, EmptyFileTests
from csvkitcat.moreutils.csvcount import CSVCount, launch_new_instance, count_csv_rows


from unittest import skip as skiptest


class TestCSVCount(CSVKitTestCase, EmptyFileTests):
    Utility = CSVCount

    def test_launch_new_instance(self):
        with patch.object(
            sys, "argv", [self.Utility.__name__.lower(), "examples/dummy.csv"]
        ):
            launch_new_instance()

    def test_basic(self):
        self.assertLines(["examples/dummy3.csv"], ["2"])

    def test_basic_no_header_row(self):
        self.assertLines(["examples/dummy3.csv", "-H"], ["3"])

    def test_skip_lines(self):
        self.assertLines(["--skip-lines", "3", "examples/test_skip_lines.csv"], ["1"])

    def test_static_csv_count_file_io(self):
        """to do: is there a reason for this method to work with a string/Path object?"""
        with open("examples/dummy4.csv") as src:
            assert count_csv_rows(src) == 4


    ### pattern count
    def test_basic_pattern_count(self):
        self.assertRows(['-P', r'\d', 'examples/dummy.csv'], [
            ['pattern','rows','cells'],
            [r'\d','1','3'],
        ])

    def test_basic_pattern_count_no_match(self):
        self.assertRows(['-P', r'[a-z]', 'examples/dummy.csv'], [
            ['pattern','rows','cells'],
            [r'[a-z]','0','0'],
        ])

    def test_only_regexes(self):
        self.assertLines(['-P', r'w|o', 'examples/pipes.csv'], [
            'pattern,rows,cells',
            'w|o,1,1'
        ])


    def test_takes_multiple_patterns(self):
        self.assertRows(['-P', '1', '-P', '2', '-P', 'Y', 'examples/dummy.csv'], [
            ['pattern','rows','cells'],
            ['1','1','1'],
            ['2','1','1'],
            ['Y','0','0'],

        ])


    @skiptest('need to design')
    def test_count_specific_cols(self):
        pass

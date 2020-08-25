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

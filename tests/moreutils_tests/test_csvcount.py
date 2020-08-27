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
        self.assertLines(
            ["examples/dummy3.csv"],
            ["rows,cells,empty_rows,empty_cells,blank_lines", "2,6,0,0,0"],
        )

    def test_basic_no_header_row(self):
        self.assertLines(
            ["examples/dummy3.csv", "-H"],
            ["rows,cells,empty_rows,empty_cells,blank_lines", "3,9,0,0,0"],
        )

    def test_basic_skip_lines(self):
        self.assertLines(
            ["--skip-lines", "3", "examples/test_skip_lines.csv"],
            ["rows,cells,empty_rows,empty_cells,blank_lines", "1,3,0,0,0"],
        )

    #############################################
    ## pattern counting
    def test_pattern_count(self):
        self.assertRows(
            ["-P", r"\d", "examples/dummy.csv"],
            [["pattern", "rows", "cells", "matches"], [r"\d", "1", "3", "3",],],
        )

    def test_pattern_count_no_match(self):
        self.assertRows(
            ["-P", r"[a-z]", "examples/dummy.csv"],
            [["pattern", "rows", "cells", "matches"], [r"[a-z]", "0", "0", "0"],],
        )

    def test_that_it_only_uses_regexes_not_literal_matches(self):
        self.assertLines(
            ["-P", r"w|o", "examples/pipes.csv"],
            ["pattern,rows,cells,matches", "w|o,1,1,3"],
        )

    def test_takes_multiple_patterns(self):
        self.assertRows(
            ["-P", "1", "-P", "2", "-P", "Y", "examples/dummy.csv"],
            [
                ["pattern", "rows", "cells", "matches"],
                ["1", "1", "1", "1"],
                ["2", "1", "1", "1"],
                ["Y", "0", "0", "0"],
            ],
        )

    def test_count_specific_cols(self):
        self.assertLines(
            ["-c", "a,c", "-P", "2", "examples/dummy5.csv"],
            ["pattern,rows,cells,matches", "2,2,4,7",],
        )

    ########################
    ### edge cases

    def test_edge_basic_when_column_is_specified(self):
        """probably not many use cases to specify -c flag without -P [PATTERN], but if
        it happens, then the result should be a subcount based on the selected columns"""

        self.assertLines(
            ["-c", "id,name", "examples/empties.csv"],
            ["rows,cells,empty_rows,empty_cells,blank_lines", "4,8,1,2,0",],
        )

    #################################
    ### Tests that verify my examples

    def test_examples_basic(self):
        self.assertLines(
            ["examples/dummy4.csv"],
            ["rows,cells,empty_rows,empty_cells,blank_lines", "4,12,0,0,0"],
        )

    def test_examples_basic_w_empties(self):
        self.assertLines(
            ["examples/empties.csv"],
            ["rows,cells,empty_rows,empty_cells,blank_lines", "4,12,1,4,0"],
        )

    def test_basic_w_blanked_lines(self):
        self.assertLines(
            ["examples/blankedlines.csv"],
            ["rows,cells,empty_rows,empty_cells,blank_lines", "3,9,0,0,4"],
        )

    def test_pattern_5letter_words(self):
        self.assertLines(
            ["-P", "[A-z]{5,}", "examples/longvals.csv"],
            ["pattern,rows,cells,matches", '"[A-z]{5,}",3,9,43'],
        )

    def test_pattern_5letter_words_column_specified(self):
        self.assertLines(
            ["-c", "description", "-P", "[A-z]{5,}", "examples/longvals.csv"],
            ["pattern,rows,cells,matches", '"[A-z]{5,}",3,3,31'],
        )

    #####
    # DEPRECATE THIS

    def test_static_csv_count_file_io(self):
        """
        todo: is there a reason for this method to work with a string/Path object?
        todo: this helper method is deprecated and not used
        """

        with open("examples/dummy4.csv") as src:
            assert count_csv_rows(src) == 4

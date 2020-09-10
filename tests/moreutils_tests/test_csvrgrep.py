#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from csvkitcat.moreutils.csvrgrep import CSVRgrep, launch_new_instance
from tests.utils import CSVKitTestCase, ColumnsTests, EmptyFileTests, NamesTests
from unittest import skip as skiptest


# class TestCSVRgrep(CSVKitTestCase, EmptyFileTests):
class TestCSVGrep(CSVKitTestCase, EmptyFileTests, ColumnsTests, NamesTests):

    Utility = CSVRgrep
    default_args = ["-E", r"\d", ""]
    columns_args = ["-E", r"\d", ""]

    def test_launch_new_instance(self):
        with patch.object(
            sys,
            "argv",
            [self.Utility.__name__.lower()]
            + self.default_args
            + ["examples/dummy.csv"],
        ):
            launch_new_instance()

    def test_skip_lines(self):
        self.assertRows(
            [
                "--skip-lines",
                "3",
                "-c",
                "1",
                "-E",
                "1",
                "",
                "examples/test_skip_lines.csv",
            ],
            [["a", "b", "c"], ["1", "2", "3"],],
        )

    def test_basic(self):
        """
        a,b,c
        1,2,3
        2,3,42
        3,4,1
        22,99,222
        """
        self.assertRows(
            ["-E", r"\d{2}", "examples/dummy5.csv"],
            [["a", "b", "c"], ["2", "3", "42"], ["22", "99", "222"]],
        )

    def test_basic_2nd_arg(self):
        """
        a,b,c
        1,2,3
        2,3,42
        3,4,1
        22,99,222
        """
        self.assertRows(
            ["-E", r"\d{2}", "", "examples/dummy5.csv"],
            [["a", "b", "c"], ["2", "3", "42"], ["22", "99", "222"]],
        )

    def test_basic_2nd_arg_cols(self):
        """
        a,b,c
        1,2,3
        2,3,42
        3,4,1
        22,99,222
        """
        self.assertRows(
            ["-E", r"\d{2}", "a,b", "examples/dummy5.csv"],
            [["a", "b", "c"], ["22", "99", "222"]],
        )

    ##############

    def test_basic_literal_match(self):
        self.assertRows(
            ["-m", "-E", r"\d{2}", "", "examples/dummy5.csv"], [["a", "b", "c"],]
        )

        self.assertRows(
            ["-m", "-E", "22", "", "examples/dummy5.csv"],
            [["a", "b", "c"], ["22", "99", "222"]],
        )

    def test_all_match(self):
        self.assertLines(
            ["-a", "-E", r"\d{2,}", "a,c", "examples/dummy5.csv"],
            ["a,b,c", "22,99,222",],
        )

    ########### multi expressions

    def test_multi_expression_basic(self):
        self.assertLines(
            ["-E", "2", "-E", r"1|3", "examples/dummy5.csv"],
            ["a,b,c", "1,2,3", "2,3,42",],
        )


    def test_multi_expression_variable_expr_args(self):
        self.assertLines(
            ["-E", "2", "-m", "-E", r"3", "b,c", "-E", "2", "examples/dummy5.csv"],
            ["a,b,c", "1,2,3", "2,3,42",],
        )

    def test_expr_col_arg_overrides_main_columns_flag(self):
        """
        if the expression has a column str other than '', then its list of column_ids to grep
        takes precedence over  -c/--columns
        """
        self.assertLines(
            ["-c", "a,c", "-E", "2", "a,b,c", "examples/dummy5.csv"],
            ["a,b,c", "1,2,3", "2,3,42", "22,99,222",],
        )

    def test_expr_col_arg_defaults_to_main_columns_flag(self):
        """
        if the expression has a blank column str, then it uses whatever -c/--columns is set to

        (and if -c is unset, then all columns are grepped)
        """
        self.assertLines(
            ["-c", "c,a", "-E", "2", "a,b,c", "-E", "2", "examples/dummy5.csv"],
            ["a,b,c", "2,3,42", "22,99,222",],
        )

        self.assertLines(
            ["-E", "2", "a,b", "-E", "3", "examples/dummy5.csv"],
            ["a,b,c", "1,2,3", "2,3,42",],
        )




    @skiptest('to do')
    def test_when_last_expr_is_single_arg_and_no_input_file(self):
        r"""
        cat data.txt | csvrgrep -E '\d{2}'

        Make sure that '\d{2}' is not taken from -E; input_file should be None in this case
        """
        pass

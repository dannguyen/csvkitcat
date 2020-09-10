#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import six

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from csvkit.exceptions import ColumnIdentifierError
from csvkitcat.moreutils.csvsed import CSVSed, launch_new_instance

from unittest import skip as skiptest
from tests.utils import CSVKitTestCase, stdin_as_string, EmptyFileTests

from io import StringIO


class TestCSVSed(CSVKitTestCase, EmptyFileTests):
    Utility = CSVSed
    default_args = ["hello", "world"]

    def test_launch_new_instance(self):
        with patch.object(
            sys,
            "argv",
            [self.Utility.__name__.lower(), "hey", "you", "examples/dummy.csv"],
        ):
            launch_new_instance()

    def test_basic_dummy(self):
        """
        Shouldn't alter headers
        """
        self.assertLines(
            [r"(\w)", r"\1!", "examples/dummy.csv"], ["a,b,c", "1!,2!,3!",]
        )

    def test_outputs_non_pattern_matches_too(self):
        self.assertLines(
            [r"([a-z])", r"\1!", "examples/tinyvals.csv"],
            ["alpha,omega", "1,9", "a!,z!", "$,%",],
        )

    def test_skip_lines(self):
        self.assertLines(
            [
                "--skip-lines",
                "3",
                "-D",
                "|",
                r"\w",
                "x",
                "examples/test_skip_lines.csv",
            ],
            ["a|b|c", "x|x|x",],
        )

    def test_column_choice(self):
        self.assertLines(
            ["-c", "b,c", r"(\w)", r"\1!", "examples/dummy.csv"], ["a,b,c", "1,2!,3!",]
        )

    def test_supports_case_insensitivity(self):
        self.assertLines(
            [r"(?i)miss", "Ms.", "examples/honorifics-fem.csv"],
            [
                "code,name",
                "1,Mrs. Smith",
                "2,Ms. Daisy",
                "3,Ms. Doe",
                "4,Mrs Miller",
                "5,Ms Lee",
                "6,Ms. maam",
            ],
        )

    def test_literal_match(self):
        self.assertLines(
            ["-m", "s.", "x.", "examples/honorifics-fem.csv"],
            [
                "code,name",
                "1,Mrx. Smith",
                "2,Miss Daisy",
                "3,Mx. Doe",
                "4,Mrs Miller",
                "5,Ms Lee",
                "6,miss maam",
            ],
        )

    def test_max_match_count(self):
        self.assertLines(
            ["--max", "2", r"(\w)", r"\1!", "examples/dummy3x.csv"],
            ["a,b,c", "1!d!,2!e!,3!f!", "1! t!x,4! t!y,5! t!z",],
        )

    def test_max_match_count_normalize_negative_val_to_default_catchall_val(self):
        self.assertLines(
            ["-m", "--max", "-99999", "s.", "x.", "examples/honorifics-fem.csv"],
            [
                "code,name",
                "1,Mrx. Smith",
                "2,Miss Daisy",
                "3,Mx. Doe",
                "4,Mrs Miller",
                "5,Ms Lee",
                "6,miss maam",
            ],
        )

    def test_hacky_strip(self):
        self.assertLines(
            [r"^\s*(.+?)\s*$", r"\1", "examples/consec_ws.csv"],
            ["id,phrase", "1,hello world", "2,good   bye", "3,a  ok",],
        )

    def test_replace_value(self):
        self.assertLines(
            ["-R", "(?i)^y", "Yeah", "examples/yes.csv"],
            ["code,value", "1,Yeah", "2,no", "3,Yeah", "4,Yeah", "5,Yeah",],
        )

    def test_replace_value_w_cap_group(self):
        ############### replace

        """
        code,value
        1,my money
        2,"my stuff, my way"
        3,your house has my car
        """
        self.assertLines(
            ["--replace", r"my (\w+)", r"Your \1!", "examples/myway.csv"],
            ["code,value", "1,Your money!", "2,Your stuff!", "3,Your car!",],
        )

    def test_like_grep(self):
        self.assertLines(
            ["-G", r"my (\w{5,})", r"Your \1!", "examples/myway.csv"],
            ["code,value", "1,Your money!", '2,"Your stuff!, my way"',],
        )

    # @skiptest('need to do test_like_grep on their own')
    def test_replace_and_like_grep(self):
        self.assertLines(
            ["-R", "-G", "(?i)^y", "Yeah", "examples/yes.csv"],
            ["code,value", "1,Yeah", "3,Yeah", "4,Yeah", "5,Yeah",],
        )

    ############ expressions

    def test_manual_expression(self):
        self.assertLines(
            ["-E", r"my (\w{5,})", r"Your \1!", "value", "examples/myway.csv"],
            [
                "code,value",
                "1,Your money!",
                '2,"Your stuff!, my way"',
                "3,your house has my car",
            ],
        )

    ##################### errors
    # class ColumnsTests(object):
    def test_invalid_column(self):
        args = ["-c", "0",] + self.default_args + ["examples/dummy.csv"]

        output_file = six.StringIO()
        utility = self.Utility(args, output_file)

        with self.assertRaises(ColumnIdentifierError):
            utility.run()

        output_file.close()

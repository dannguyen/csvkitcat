#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import six

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from csvkitcat.moreutils.csvnorm import CSVNorm, launch_new_instance
from tests.utils import (
    CSVKitTestCase,
    EmptyFileTests,
    stdin_as_string,
    ColumnsTests,
    NamesTests,
)


class TestCSVNorm(CSVKitTestCase, ColumnsTests, EmptyFileTests, NamesTests):
    Utility = CSVNorm

    def test_launch_new_instance(self):
        with patch.object(
            sys, "argv", [self.Utility.__name__.lower(), "examples/dummy.csv"]
        ):
            launch_new_instance()

    def test_basic_dummy(self):
        """
        Shouldn't alter a file with no whitespace/nonprintable characters whatsoever
        """
        self.assertLines(["examples/dummy.csv"], ["a,b,c", "1,2,3",])

    def test_basic_tab_normalize(self):
        self.assertRows(
            ["examples/tabs.wtf"],
            [
                ["id", "val"],
                ["1", "a"],
                ["2", "tab b"],
                ["3", "c 2tab d"],
                ["4", "spaces 4x"],
            ],
        )

    def test_disable_strip(self):
        """
        id,text
        "1","hey"
        "2  ","hello  world  "
        "   3 ","    bye    now "
        """
        self.assertRows(
            ["--no-strip", "examples/strips.csv"],
            [
                ["id", "text"],
                ["1", "hey"],
                ["2 ", "hello world "],
                [" 3 ", " bye now "],
            ],
        )

    def test_disable_squeeze_space(self):
        self.assertRows(
            ["--squeeze", "l", "examples/strips.csv"],
            [["id", "text"], ["1", "hey"], ["2", "hello  world"], ["3", "bye    now"],],
        )

    def test_keep_consecutive_whitespace_oldtest(self):
        self.assertLines(
            ["examples/consec_ws.csv", "--SX"],
            ["id,phrase", "1,hello world", "2,good   bye", "3,a  ok"],
        )

    def test_disable_strip_and_squeeze(self):
        self.assertLines(
            ["--SX", "--no-strip", "examples/strips.csv"],
            [
                """id,text""",
                """1,hey""",
                """2  ,hello  world  """,
                """   3 ,    bye    now """,
            ],
        )

    def test_default_norm(self):
        """
        norm with all the works
        """
        self.assertLines(
            ["examples/mess.csv"],
            ["code,name", "1,Dan", "0 2,Billy Bob", "0003,..Who..?", "4,Mr. R obot",],
        )

    def test_norm_does_not_affect_headers(self):
        self.assertLines(
            ["examples/mess_head.csv", "-u", "0"],
            [""" code   ," the  first""", ''' name   "''', "1,Dan", "0 2,Billy Bob",],
        )

    def test_kill_lines(self):
        self.assertLines(
            ["examples/linebreaks.csv",],
            ["id,speech", """1,hey you folks whats up?""",],
        )

    def test_keep_lines(self):
        self.assertLines(
            ["examples/linebreaks.csv", "--keep-lines"],
            ["id,speech", """1,"hey""", "you", "folks", 'whats up?"',],
        )

    def test_change_case_upper(self):
        self.assertLines(
            ["-C", "upper", "examples/statecodes.csv"],
            ["code,name", "IA,IOWA", "RI,RHODE ISLAND", "TN,TENNESSEE",],
        )

    def test_change_case_lower(self):
        self.assertLines(
            ["-C", "lower", "examples/statecodes.csv"],
            ["code,name", "ia,iowa", "ri,rhode island", "tn,tennessee",],
        )

    ######## test column choice
    def test_selected_columns_normd(self):
        self.assertLines(
            ["examples/consec_ws.csv", "-c", "id"],
            ["id,phrase", "1,hello world", "2,good   bye", "3,  a  ok",],
        )

    def test_selected_columns_normd_w_options(self):
        """since Column 1 is not selected, no stripping of `id` is done"""
        self.assertLines(
            ["examples/consec_ws.csv", "-c", "2", "--SX"],
            ["id,phrase", "1,hello world", "2,good   bye", " 3  ,a  ok"],
        )

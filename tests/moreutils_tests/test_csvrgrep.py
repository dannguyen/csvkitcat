#!/usr/bin/env python
# -*- coding: utf-8 -*-

import contextlib
from io import StringIO
import sys
from multiprocessing import Process

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch


from csvkitcat.moreutils.csvrgrep import CSVRgrep, launch_new_instance
from csvkitcat.exceptions import *

from tests.utils import CSVKitTestCase, ColumnsTests, EmptyFileTests, NamesTests
from unittest import skip as skiptest
from subprocess import Popen, PIPE


# class TestCSVRgrep(CSVKitTestCase, EmptyFileTests):
class TestCSVGrep(CSVKitTestCase, EmptyFileTests, NamesTests, ColumnsTests):

    Utility = CSVRgrep
    default_args = [
        "-E",
        r"\d",
        "examples/dummy.csv",
    ]
    columns_args = [
        "-c",
        "1,2",
        "-E",
        "1",
    ]

    def test_launch_new_instance(self):
        with patch.object(
            sys,
            "argv",
            [self.Utility.__name__.lower()] + self.default_args
            # + ["examples/dummy.csv"],
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

    def test_when_last_expr_is_single_arg_and_no_input_file(self):
        r"""
        cat data.txt | csvrgrep -E '\d{2}'

        Make sure that '\d{2}' is not taken from -E; input_file should be None in this case
        """
        p1 = Popen(["cat", "examples/dummy5.csv"], stdout=PIPE)
        p2 = Popen(["csvrgrep", "-E", "1"], stdin=p1.stdout, stdout=PIPE)
        p1.stdout.close()
        p1.wait()
        txt = p2.communicate()[0].decode("utf-8")
        p2.wait()

        lines = txt.splitlines()
        self.assertEqual(lines, ["a,b,c", "1,2,3", "3,4,1",])

    ##### error stuff

    def test_error_when_no_expressions(self):
        ioerr = StringIO()
        with contextlib.redirect_stderr(ioerr):
            with self.assertRaises(SystemExit) as e:
                u = self.get_output(["examples/dummy4.csv"])

        self.assertEqual(e.exception.code, 2)
        self.assertIn("Must specify at least one -E/--expr", ioerr.getvalue())

    def test_error_when_expression_has_0_args(self):
        ioerr = StringIO()
        with contextlib.redirect_stderr(ioerr):
            with self.assertRaises(SystemExit) as e:
                u = self.get_output(["-E", "-m", "examples/dummy.csv"])

        self.assertEqual(e.exception.code, 2)
        self.assertIn("-E/--expr requires at least 1 argument", ioerr.getvalue())

    @skiptest("because I dont know how to deal with stdin.isatty holdup")
    def test_error_when_final_expression_eats_up_input_path(self):
        ioerr = StringIO()
        old_stdin = sys.stdin

        with contextlib.redirect_stderr(ioerr):
            # with self.assertRaises(SystemExit) as e:
            args = ["-E", "1", "-E", "2", "-E", "examples/dummy.csv"]
            # p = Process(target=self.get_output, args=(args,))
            # p.start()
            sys.stdin = StringIO("a,b,c\n1,2,3\n")
            # p.join()

            self.assertIn("WARNING", ioerr.getvalue())

        # self.assertEqual(e.exception.code, 2)
        # clean up stdin
        sys.stdin = oldstdin
        exit

    def test_error_when_expression_has_more_than_2_args(self):
        ioerr = StringIO()
        with contextlib.redirect_stderr(ioerr):
            with self.assertRaises(SystemExit) as e:
                u = self.get_output(["-E", "a", "b", "c", "examples/dummy.csv"])

        self.assertEqual(e.exception.code, 2)
        self.assertIn("-E/--expr takes 1 or 2 arguments, not 3:", ioerr.getvalue())

    ########## future work

    def test_multi_expressions_are_ANDed_not_ORed(self):

        self.assertLines(
            [
                "--expr",
                r"^[HL]",
                "speaker",
                "--expr",
                r"[^1]",
                "act",
                "--expr",
                r"\w{6,}",
                "examples/hamlet.csv",
            ],
            ["act,scene,speaker,lines", "4,7,Laertes,Know you the hand?",],
        )

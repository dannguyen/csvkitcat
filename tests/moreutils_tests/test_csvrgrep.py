#!/usr/bin/env python
# -*- coding: utf-8 -*-


import contextlib
from io import StringIO
from subprocess import Popen, PIPE
import sys

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch


from csvkitcat.moreutils.csvrgrep import CSVRgrep, launch_new_instance
from csvkitcat.exceptions import *

from tests.utils import CSVKitTestCase, ColumnsTests, EmptyFileTests, NamesTests
from unittest import skip as skiptest
from subprocess import Popen, PIPE


# class TestCSVRgrep(CSVKitTestCase, EmptyFileTests, NamesTests, ColumnsTests):
class TestCSVRgrep(CSVKitTestCase, EmptyFileTests, NamesTests):

    Utility = CSVRgrep
    default_args = [
        r"\d",
        "examples/dummy.csv",
    ]
    columns_args = [
        r"\d+",
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
            ["--skip-lines", "3", "-c", "a,b", "1", "examples/test_skip_lines.csv",],
            [["a", "b", "c"], ["1", "2", "3"],],
        )

    def test_invalid_column_modified(self):
        """
        todo: figure out a way to robustly handle intermixed optional and positional args
        """
        args = ["-c", "0"] + getattr(self, "columns_args", []) + ["examples/dummy.csv"]

        import six

        output_file = six.StringIO()
        utility = self.Utility(args, output_file)

        with self.assertRaises(ColumnIdentifierError):
            utility.run()

        output_file.close()

    def test_basic(self):
        """
        a,b,c
        1,2,3
        2,3,42
        3,4,1
        22,99,222
        """
        self.assertRows(
            [r"\d{2}", "examples/dummy5.csv"],
            [["a", "b", "c"], ["2", "3", "42"], ["22", "99", "222"]],
        )

    def test_basic_column_arg(self):
        """
        a,b,c
        1,2,3
        2,3,42
        3,4,1
        22,99,222
        """
        self.assertRows(
            [r"3|22", "examples/dummy5.csv", "-c", "b,c",],
            [["a", "b", "c"], ["1", "2", "3"], ["2", "3", "42"], ["22", "99", "222"]],
        )

    def test_two_patterns(self):
        """
        a,b,c
        1,2,3
        2,3,42
        3,4,1
        22,99,222
        """
        self.assertRows(
            ["-c", "b,c", "3|22", "-E", r"^\d$", "examples/dummy5.csv",],
            [["a", "b", "c"], ["1", "2", "3"], ["2", "3", "42"]],
        )

    def test_multi_patterns_explicit_col_arg(self):
        """

        1,2,3
        2,3,42
        3,4,1
        22,99,222
        """
        self.assertLines(
            ["-c", "b,c", "3|22", "-E", r"^\d$", "c", "examples/dummy5.csv",],
            ["a,b,c", "1,2,3"],
        )

    ##############

    def test_basic_literal_match(self):
        self.assertRows(["-m", r"\d{2}", "examples/dummy5.csv"], [["a", "b", "c"],])

        self.assertRows(
            ["-m", "-c", "c", "22", "examples/dummy5.csv"],
            [["a", "b", "c"], ["22", "99", "222"]],
        )

    def test_all_match(self):
        """TODO: can't mix and match positional and optional args?"""
        self.assertLines(
            ["-a", "-c", "a,c", r"\d{2,}", "examples/dummy5.csv"],
            ["a,b,c", "22,99,222",],
        )

    ########### multi expressions

    def test_multi_expression_basic(self):
        self.assertLines(
            ["2", "-E", r"1|3", "examples/dummy5.csv"], ["a,b,c", "1,2,3", "2,3,42",],
        )

    def test_multi_expression_variable_expr_args(self):
        self.assertLines(
            ["2", "-m", "-E", r"3", "b,c", "-E", "2", "examples/dummy5.csv"],
            ["a,b,c", "1,2,3", "2,3,42",],
        )

    def test_expr_col_arg_overrides_main_columns_flag(self):
        """
        if the expression has a column str other than '', then its list of column_ids to grep
        takes precedence over  -c/--columns
        """
        self.assertLines(
            ["-c", "a,c", "2", "-E", r"\d{2,}", "b", "examples/dummy5.csv"],
            ["a,b,c", "22,99,222",],
        )

    def test_expr_col_arg_defaults_to_main_columns_flag(self):
        """
        if the expression has a blank column str, then it uses whatever -c/--columns is set to

        (and if -c is unset, then all columns are grepped)

        1,2,3
        2,3,42
        3,4,1
        22,99,222
        """
        self.assertLines(
            [
                "-c",
                "c,a",
                "2",
                "-E",
                r"\d{2,}",
                "a,b,c",
                "-E",
                "4",
                "examples/dummy5.csv",
            ],
            ["a,b,c", "2,3,42",],
        )

        self.assertLines(
            ["-c", "a,b", "2", "-E", "3", "examples/dummy5.csv"], ["a,b,c", "2,3,42",],
        )

    def test_when_single_pattern_and_no_input_file(self):
        r"""
        cat data.txt | csvrgrep '\d{2}'

        Make sure that '\d{2}' is not taken as input file name; input_file should be None in this case
        """
        p1 = Popen(["cat", "examples/dummy5.csv"], stdout=PIPE)
        p2 = Popen(["csvrgrep", "4",], stdin=p1.stdout, stdout=PIPE)
        p1.stdout.close()
        p1.wait()
        txt = p2.communicate()[0].decode("utf-8")
        p2.wait()

        lines = txt.splitlines()
        self.assertEqual(lines, ["a,b,c", "2,3,42", "3,4,1",])

    def test_when_last_expr_has_just_one_arg_and_no_input_file(self):
        r"""
        cat data.txt | csvrgrep -E '\d{2}'

        Make sure that '\d{2}' is not taken from -E; input_file should be None in this case
        """
        p1 = Popen(["cat", "examples/dummy5.csv"], stdout=PIPE)
        p2 = Popen(["csvrgrep", "1", "-E", "1"], stdin=p1.stdout, stdout=PIPE)
        p1.stdout.close()
        p1.wait()
        txt = p2.communicate()[0].decode("utf-8")
        p2.wait()

        lines = txt.splitlines()
        self.assertEqual(lines, ["a,b,c", "1,2,3", "3,4,1",])

    ##############################
    # error stuff

    def test_error_when_no_pattern_and_no_input_file(self):
        ioerr = StringIO()
        with contextlib.redirect_stderr(ioerr):
            with self.assertRaises(SystemExit) as e:
                u = self.get_output([])

        self.assertEqual(e.exception.code, 2)
        self.assertIn("the following arguments are required: PATTERN", ioerr.getvalue())

    def test_error_when_no_pattern_but_additional_expressions(self):
        """"todo, maybe redundant"""
        ioerr = StringIO()
        with contextlib.redirect_stderr(ioerr):
            with self.assertRaises(SystemExit) as e:
                u = self.get_output(["-E", "1", "examples/dummy.csv"])

        self.assertEqual(e.exception.code, 2)
        self.assertIn("the following arguments are required: PATTERN", ioerr.getvalue())

    def test_error_when_expression_has_0_args(self):
        ioerr = StringIO()
        with contextlib.redirect_stderr(ioerr):
            with self.assertRaises(SystemExit) as e:
                u = self.get_output(["-E", "-m", "PATTERN", "examples/dummy.csv"])

        self.assertEqual(e.exception.code, 2)
        self.assertIn("-E/--expr takes 1 or 2 arguments, not 0:", ioerr.getvalue())

    def test_error_when_expression_has_more_than_2_args(self):
        ioerr = StringIO()
        with contextlib.redirect_stderr(ioerr):
            with self.assertRaises(SystemExit) as e:
                u = self.get_output(
                    ["PATTERN", "examples/dummy.csv", "-E", "a", "b", "c",]
                )

        self.assertEqual(e.exception.code, 2)
        self.assertIn("-E/--expr takes 1 or 2 arguments, not 3:", ioerr.getvalue())

    def test_no_error_when_expression_has_1_args_and_piped_input(self):
        p1 = Popen(["cat", "examples/dummy.csv",], stdout=PIPE)
        p2 = Popen(["csvrgrep", "2|1", "-E", "1|2",], stdin=p1.stdout, stdout=PIPE)
        p1.stdout.close()
        p1.wait()
        txt = p2.communicate()[0].decode("utf-8")
        p2.wait()
        self.assertEqual(txt.splitlines(), ["a,b,c", "1,2,3"])

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

    ########## future work

    def test_multi_expressions_are_ANDed_not_ORed(self):

        self.assertLines(
            [
                ".+",
                "examples/hamlet.csv",
                "--expr",
                r"^[HL]",
                "speaker",
                "--expr",
                r"[^1]",
                "act",
                "--expr",
                r"\w{6,}",
            ],
            ["act,scene,speaker,lines", "4,7,Laertes,Know you the hand?",],
        )

    ###########
    ### special stuff

    def test_pattern_arg_has_leading_hyphen_causes_error(self):
        ioerr = StringIO()
        with contextlib.redirect_stderr(ioerr):
            with self.assertRaises(SystemExit) as e:
                u = self.get_output([r"-\d", "examples/ledger.csv"])

        self.assertEqual(e.exception.code, 2)
        self.assertIn(r"unrecognized arguments: -\d", ioerr.getvalue())
        # todo later
        # self.assertIn(rf"""If you are trying to match a pattern that begins with a hyphen, put a backslash before that hyphen, e.g. '\-\d' """, ioerr.getvalue())

    def test_pattern_arg_has_leading_hyphen_escaped(self):
        self.assertLines(
            [r"\-\d", "examples/ledger.csv",],
            [
                "id,name,revenue,gross",
                # '001,apples,21456,$3210.45',
                # '002,bananas,"2,442","-$1,234"',
                # '003,cherries,"$9,700.55","($7.90)"',
                # '004,dates,4 102 765.33,18 765',
                # '005,eggplants,"$3,987",$501',
                # '006,figs,"$30,333","(777.66)"',
                '006,grapes,"154,321.98","-32,654"',
            ],
        )

    def test_pattern_arg_has_leading_hyphen_double_escaped(self):
        self.assertLines(
            [r"\\-\d", "examples/ledger.csv",],
            [
                "id,name,revenue,gross",
                # '001,apples,21456,$3210.45',
                # '002,bananas,"2,442","-$1,234"',
                # '003,cherries,"$9,700.55","($7.90)"',
                # '004,dates,4 102 765.33,18 765',
                # '005,eggplants,"$3,987",$501',
                # '006,figs,"$30,333","(777.66)"',
            ],
        )

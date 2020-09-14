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

from csvkitcat.exceptions import ColumnIdentifierError
from csvkitcat.moreutils.csvsed import CSVSed, launch_new_instance

from unittest import skip as skiptest
from tests.utils import CSVKitTestCase, stdin_as_string, EmptyFileTests


class TestCSVSed(CSVKitTestCase):
    Utility = CSVSed
    default_args = ["-E", "hello", "world"]

    def test_launch_new_instance(self):
        with patch.object(
            sys,
            "argv",
            [self.Utility.__name__.lower(), *self.default_args, "examples/dummy.csv"],
        ):
            launch_new_instance()

    def test_basic_dummy(self):
        """
        Shouldn't alter headers
        """
        self.assertLines(
            ["-E", r"(\w)", r"\1!", "examples/dummy.csv"], ["a,b,c", "1!,2!,3!",]
        )

    def test_basic_dummy_expr_full_args(self):
        self.assertLines(
            ["--expr", r"(\w)", r"\1!", "1-3", "examples/dummy.csv"],
            ["a,b,c", "1!,2!,3!",],
        )

    def test_outputs_non_pattern_matches_too(self):
        self.assertLines(
            ["-E", r"([a-z])", r"\1!", "examples/tinyvals.csv"],
            ["alpha,omega", "1,9", "a!,z!", "$,%",],
        )

    def test_skip_lines(self):
        """redundant"""
        self.assertLines(
            ["--skip-lines", "3", "-E", r"\w", "x", "examples/test_skip_lines.csv",],
            ["a,b,c", "x,x,x",],
        )

    def test_column_choice(self):
        self.assertLines(
            ["-c", "b,c", "--expr", r"(\w)", r"\1!", "examples/dummy.csv"],
            ["a,b,c", "1,2!,3!",],
        )

        # expr column choice overrides global -c
        self.assertLines(
            ["-c", "b,c", "--expr", r"(\w)", r"\1!", "a,b", "examples/dummy.csv"],
            ["a,b,c", "1!,2!,3",],
        )

    def test_supports_case_insensitivity(self):
        self.assertLines(
            ["-E", r"(?i)miss", "Ms.", "examples/honorifics-fem.csv"],
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
            ["-m", "-E", "s.", "x.", "examples/honorifics-fem.csv"],
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
            ["--max", "2", "-E", r"(\w)", r"\1!", "examples/dummy3x.csv"],
            ["a,b,c", "1!d!,2!e!,3!f!", "1! t!x,4! t!y,5! t!z",],
        )

    def test_max_match_count_normalize_negative_val_to_default_catchall_val(self):
        self.assertLines(
            ["-m", "--max", "-99999", "-E", "s.", "x.", "examples/honorifics-fem.csv"],
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
            ["-E", r"^\s*(.+?)\s*$", r"\1", "examples/consec_ws.csv"],
            ["id,phrase", "1,hello world", "2,good   bye", "3,a  ok",],
        )

    def test_replace_value(self):
        self.assertLines(
            ["-R", "-E", "(?i)^y", "Yeah", "examples/yes.csv"],
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
            ["--replace", "-E", r"my (\w+)", r"Your \1!", "examples/myway.csv"],
            ["code,value", "1,Your money!", "2,Your stuff!", "3,Your car!",],
        )

    def test_like_grep_mode(self):
        self.assertLines(
            ["-G", "-E", r"my (\w{5,})", r"Your \1!", "examples/myway.csv"],
            ["code,value", "1,Your money!", '2,"Your stuff!, my way"',],
        )

    # @skiptest('need to do test_like_grep on their own')
    def test_replace_and_like_grep(self):
        self.assertLines(
            ["-R", "-G", "-E", "(?i)^y", "Yeah", "examples/yes.csv"],
            ["code,value", "1,Yeah", "3,Yeah", "4,Yeah", "5,Yeah",],
        )

    ############ expressions
    # @skiptest('FIX ASAP')
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

    def test_manual_multiple_expression(self):
        self.assertLines(
            [
                "-E",
                r"my (\w{5,})",
                r"Your \1!",
                "value",
                "-E",
                r"(\w)",
                r"00\1",
                "code",
                "examples/myway.csv",
            ],
            [
                "code,value",
                "001,Your money!",
                '002,"Your stuff!, my way"',
                "003,your house has my car",
            ],
        )

    ##################### errors
    # class ColumnsTests(object):
    def test_invalid_column(self):
        args = ["-c", "0",] + self.default_args + ["examples/dummy.csv"]

        output_file = StringIO()
        utility = self.Utility(args, output_file)

        with self.assertRaises(ColumnIdentifierError):
            utility.run()

        output_file.close()

    ########## order of operations

    # [
    # 'id,col_a,col_b',
    # '1,hello,world',
    # '2,Hey,you',
    # '3,1,2',
    # '4,9999999,777',
    # '5,OK,Boomer',
    # '6,memory,"Person,woman,man,camera,TV"',]

    def test_order_expressions(self):
        self.assertLines(
            [
                "-E",
                r"^(.{1,2})$",
                r"\1\1",
                "col_a,col_b",
                "-E",
                r"^(.{4})$",
                r"_\1_",
                "id,col_a,col_b",
                "-E",
                r"^(.{6})",
                r"\1, oxford and etc.",
                "col_a",
                "examples/ab.csv",
            ],
            [
                "id,col_a,col_b",
                "1,hello,world",
                "2,Hey,you",
                "3,11,22",
                '4,"999999, oxford and etc.9",777',
                '5,"_OKOK_, oxford and etc.",Boomer',
                '6,"memory, oxford and etc.","Person,woman,man,camera,TV"',
            ],
        )

    def test_order_expressions_literal(self):
        self.assertLines(
            [
                "--match-literal",
                "-E",
                "e",
                "x",
                "col_a,col_b",
                "-E",
                "o",
                "e",
                "col_a,col_b",
                "-E",
                "er",
                "oz",
                "col_a,col_b",
                "examples/ab.csv",
            ],
            [
                "id,col_a,col_b",
                "1,hxlle,wozld",
                "2,Hxy,yeu",
                "3,1,2",
                "4,9999999,777",
                "5,OK,Beemxr",
                '6,mxmozy,"Pxrsen,weman,man,camxra,TV"',
            ],
        )

    def test_order_expressions_plus_grep_mode(self):
        """
        grep_testing happens BEFORE the transformation, thus lines that are
        transformed by the first expression and into something that matches the second
        expression pattern will NOT be returned
        """

        self.assertLines(
            [
                "-E",
                r"^(\d{2,4})$",
                r"\1\1",
                "-G",
                "-E",
                r"(\d{2})",
                r"_\1_",
                "col_a,col_b",
                "examples/ab.csv",
            ],
            [
                "id,col_a,col_b",
                # '1,hello,world',
                # '2,Hey,you',
                # '3,1,2',
                "4,_99__99__99_9,_77__77__77_",
                # '5,OK,Boomer',
                # '6,memory,"Person,woman,man,camera,TV"',
            ],
        )

    def test_multiple_expressions_like_grep_are_ANDed_not_ORed(self):
        self.assertLines(
            [
                # '-E', 'hey', 'hello',
                "-E",
                "(?i)hello|hey",
                "Goodbye",
                "-G",
                "-E",
                r".{5,}",
                r"nada",
                "col_b",  # the ANDed expression excludes row 2
                "-E",
                r"(\d+)",
                r"\1+",  # this is completely ineffectual because of the order of grepping
                "examples/ab.csv",
            ],
            [
                "id,col_a,col_b",
                "1+,Goodbye,nada",
                # '2,Hey,you',
                # '3,1,2',
                # '4,9999999+,777+',
                # '5,OK,Boomer',
                # '6,memory,"Person,woman,man,camera,TV"',
            ],
        )

    ##############################
    # error stuff

    def test_error_when_no_expressions(self):
        ioerr = StringIO()
        with contextlib.redirect_stderr(ioerr):
            with self.assertRaises(SystemExit) as e:
                u = self.get_output(["examples/dummy4.csv"])

        self.assertEqual(e.exception.code, 2)
        self.assertIn(
            "the following arguments are required: -E/--expr", ioerr.getvalue()
        )

    def test_error_when_expression_has_0_args(self):
        ioerr = StringIO()
        with contextlib.redirect_stderr(ioerr):
            with self.assertRaises(SystemExit) as e:
                u = self.get_output(["-E", "-m", "examples/dummy.csv"])

        self.assertEqual(e.exception.code, 2)
        self.assertIn(
            f"-E/--expr takes 2 or 3 arguments; you provided 0:", ioerr.getvalue()
        )

    def test_error_when_expression_has_1_arg(self):
        ioerr = StringIO()
        with contextlib.redirect_stderr(ioerr):
            with self.assertRaises(SystemExit) as e:
                u = self.get_output(["-E", "a", "-m", "examples/dummy.csv"])

        self.assertEqual(e.exception.code, 2)
        self.assertIn(
            "-E/--expr takes 2 or 3 arguments; you provided 1: ['a']", ioerr.getvalue()
        )

    def test_error_when_expression_has_more_than_3_args(self):
        ioerr = StringIO()
        with contextlib.redirect_stderr(ioerr):
            with self.assertRaises(SystemExit) as e:
                u = self.get_output(["-E", "a", "b", "c", "d", "examples/dummy.csv"])

        self.assertEqual(e.exception.code, 2)
        self.assertIn(
            "-E/--expr takes 2 or 3 arguments; you provided 4: ['a', 'b', 'c', 'd']",
            ioerr.getvalue(),
        )

    def test_no_error_when_expression_has_2_args_and_piped_input(self):
        p1 = Popen(["cat", "examples/dummy.csv",], stdout=PIPE)
        p2 = Popen(["csvsed", "-E", "(1|2)", r"\1x"], stdin=p1.stdout, stdout=PIPE)
        p1.stdout.close()
        p1.wait()
        txt = p2.communicate()[0].decode("utf-8")
        p2.wait()
        self.assertEqual(txt.splitlines(), ["a,b,c", "1x,2x,3"])

    @skiptest("because I dont know how to deal with stdin.isatty holdup")
    def test_error_when_final_expression_eats_up_input_path(self):
        ioerr = StringIO()
        old_stdin = sys.stdin

        with contextlib.redirect_stderr(ioerr):
            # with self.assertRaises(SystemExit) as e:
            args = ["-E", "1", "2", "examples/dummy.csv"]
            # p = Process(target=self.get_output, args=(args,))
            # p.start()
            sys.stdin = StringIO("a,b,c\n1,2,3\n")
            # p.join()

            self.assertIn("WARNING", ioerr.getvalue())

        # self.assertEqual(e.exception.code, 2)
        # clean up stdin
        sys.stdin = oldstdin
        exit

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

from csvkitcat import __version__
from csvkitcat.moreutils.csvflatten import (
    CSVFlatten,
    launch_new_instance,
    DEFAULT_EOR_MARKER,
)
from tests.utils import CSVKitTestCase, EmptyFileTests, stdin_as_string


class TestCSVFlatten(CSVKitTestCase, EmptyFileTests):
    Utility = CSVFlatten

    def test_launch_new_instance(self):
        with patch.object(
            sys, "argv", [self.Utility.__name__.lower(), "examples/dummy.csv"]
        ):
            launch_new_instance()

    def test_transformed_structure(self):
        """
        a,b,c
        1,2,3
        """
        self.assertLines(
            ["examples/dummy.csv"], ["fieldname,value", "a,1", "b,2", "c,3",]
        )

    def test_version(self):
        p1 = Popen(["csvflatten", "--version"], stdout=PIPE)
        # p1.stdout.close()
        p1.wait()
        txt = p1.communicate()[0].decode("utf-8")
        self.assertEqual(txt.splitlines()[0], f"csvkitcat.csvflatten ({__version__})")

        # p1 = Popen(["csvflatten", "-L", "20", "examples/hamlet.csv"], stdout=PIPE)
        # p2 = Popen(["csvlook"], stdin=p1.stdout, stdout=PIPE)
        # p1.stdout.close()
        # p1.wait()
        # txt = p2.communicate()[0].decode("utf-8")
        # p2.wait()

    """
# linebreaks.csv
id,speech
1,"
hey
you
folks


whats  up? "
    """

    def test_newline_handling(self):
        """internal newlines are preserved, but leading/trailing newlines and spaces are stripped"""
        self.assertLines(
            ["examples/linebreaks.csv",],
            [
                "fieldname,value",
                "id,1",
                "speech,hey",
                ",you",
                ",folks",
                ",",
                ",",
                ",whats  up?",
            ],
        )

    def test_skip_lines(self):
        self.assertLines(
            ["--skip-lines", "3", "examples/test_skip_lines.csv"],
            ["fieldname,value", "a,1", "b,2", "c,3",],
        )

    def test_forced_quoting_in_chop_length_mode(self):
        self.assertLines(
            ["examples/dummy.csv", "--chop-length", "42",],
            ['"fieldname","value"', '"a","1"', '"b","2"', '"c","3"',],
        )

        self.assertLines(
            ["examples/dummy.csv", "-L", "42",],
            ['"fieldname","value"', '"a","1"', '"b","2"', '"c","3"',],
        )

    ## X-chop
    def test_x_chop(self):
        self.assertLines(
            ["examples/statecodes.csv", "-L", "5"],
            [
                '"fieldname","value"',
                '"code","IA"',
                '"name","Iowa"',
                f'"{DEFAULT_EOR_MARKER}",""',
                '"code","RI"',
                '"name","Rhode"',
                '""," Isla"',
                '"","nd"',
                f'"{DEFAULT_EOR_MARKER}",""',
                '"code","TN"',
                '"name","Tenne"',
                '"","ssee"',
            ],
        )

    def test_x_chop_field_label(self):
        self.assertLines(
            ["examples/statecodes.csv", "-L", "5", "--chop-labels"],
            [
                '"fieldname","value"',
                '"code","IA"',
                '"name","Iowa"',
                f'"{DEFAULT_EOR_MARKER}",""',
                '"code","RI"',
                '"name","Rhode"',
                '"name~1"," Isla"',
                '"name~2","nd"',
                f'"{DEFAULT_EOR_MARKER}",""',
                '"code","TN"',
                '"name","Tenne"',
                '"name~1","ssee"',
            ],
        )

        """same test, but with alt label"""
        self.assertLines(
            ["examples/statecodes.csv", "-L", "5", "-B"],
            [
                '"fieldname","value"',
                '"code","IA"',
                '"name","Iowa"',
                f'"{DEFAULT_EOR_MARKER}",""',
                '"code","RI"',
                '"name","Rhode"',
                '"name~1"," Isla"',
                '"name~2","nd"',
                f'"{DEFAULT_EOR_MARKER}",""',
                '"code","TN"',
                '"name","Tenne"',
                '"name~1","ssee"',
            ],
        )

    ## end of record marker/separator
    def test_end_of_record_marker_default(self):
        """
        alpha,omega
        1,9
        a,z
        $,%
        """
        self.assertLines(
            ["examples/tinyvals.csv",],
            [
                """fieldname,value""",
                """alpha,1""",
                """omega,9""",
                f"""{DEFAULT_EOR_MARKER},""",
                """alpha,a""",
                """omega,z""",
                f"""{DEFAULT_EOR_MARKER},""",
                """alpha,$""",
                """omega,%""",
            ],
        )

    def test_no_end_of_record_marker(self):
        self.assertLines(
            ["examples/tinyvals.csv", "--eor", ""],
            [
                """fieldname,value""",
                """alpha,1""",
                """omega,9""",
                """alpha,a""",
                """omega,z""",
                """alpha,$""",
                """omega,%""",
            ],
        )
        self.assertLines(
            ["examples/tinyvals.csv", "-E", "none"],
            [
                """fieldname,value""",
                """alpha,1""",
                """omega,9""",
                """alpha,a""",
                """omega,z""",
                """alpha,$""",
                """omega,%""",
            ],
        )

    def test_custom_end_of_record_marker(self):
        self.assertLines(
            ["examples/tinyvals.csv", "-E", "False"],
            [
                """fieldname,value""",
                """alpha,1""",
                """omega,9""",
                f"""False,""",
                """alpha,a""",
                """omega,z""",
                f"""False,""",
                """alpha,$""",
                """omega,%""",
            ],
        )

        # all-caps NONE is NOT treated as "none"
        self.assertLines(
            ["examples/tinyvals.csv", "-E", "NONE"],
            [
                """fieldname,value""",
                """alpha,1""",
                """omega,9""",
                f"""NONE,""",
                """alpha,a""",
                """omega,z""",
                f"""NONE,""",
                """alpha,$""",
                """omega,%""",
            ],
        )

    #################################
    ### Tests that verify my examples

    def test_regular_hamlet_w_csvlook(self):
        p1 = Popen(["csvflatten", "examples/hamlet.csv"], stdout=PIPE)
        p2 = Popen(["csvlook"], stdin=p1.stdout, stdout=PIPE)
        p1.stdout.close()
        p1.wait()
        txt = p2.communicate()[0].decode("utf-8")
        p2.wait()

        assert (
            txt.strip()
            == """
| fieldname | value                                          |
| --------- | ---------------------------------------------- |
| act       | 1                                              |
| scene     | 5                                              |
| speaker   | Horatio                                        |
| lines     | Propose the oath, my lord.                     |
| ~~~~~~~~~ |                                                |
| act       | 1                                              |
| scene     | 5                                              |
| speaker   | Hamlet                                         |
| lines     | Never to speak of this that you have seen,     |
|           | Swear by my sword.                             |
| ~~~~~~~~~ |                                                |
| act       | 1                                              |
| scene     | 5                                              |
| speaker   | Ghost                                          |
| lines     | [Beneath] Swear.                               |
| ~~~~~~~~~ |                                                |
| act       | 3                                              |
| scene     | 4                                              |
| speaker   | Gertrude                                       |
| lines     | O, speak to me no more;                        |
|           | These words, like daggers, enter in mine ears; |
|           | No more, sweet Hamlet!                         |
| ~~~~~~~~~ |                                                |
| act       | 4                                              |
| scene     | 7                                              |
| speaker   | Laertes                                        |
| lines     | Know you the hand?                             |""".strip()
        )

    def test_chopped_hamlet_w_csvlook(self):
        p1 = Popen(["csvflatten", "-L", "20", "examples/hamlet.csv"], stdout=PIPE)
        p2 = Popen(["csvlook"], stdin=p1.stdout, stdout=PIPE)
        p1.stdout.close()
        p1.wait()
        txt = p2.communicate()[0].decode("utf-8")
        p2.wait()

        self.assertEqual(
            txt.splitlines()[-12:],
            """
| lines     | O, speak to me no mo |
|           | re;                  |
|           | These words, like da |
|           | ggers, enter in mine |
|           |  ears;               |
|           | No more, sweet Hamle |
|           | t!                   |
| ~~~~~~~~~ |                      |
| act       | 4                    |
| scene     | 7                    |
| speaker   | Laertes              |
| lines     | Know you the hand?   |""".strip().splitlines(),
        )

    ### errors
    def test_error_when_chop_label_but_no_chop_length(self):
        ioerr = StringIO()
        with contextlib.redirect_stderr(ioerr):
            with self.assertRaises(SystemExit) as e:
                u = self.get_output(["--chop-label", "examples/dummy4.csv"])

        self.assertEqual(e.exception.code, 2)
        self.assertIn(
            "-B/--chop-label is an invalid option unless -L/--chop-length is specified",
            ioerr.getvalue(),
        )

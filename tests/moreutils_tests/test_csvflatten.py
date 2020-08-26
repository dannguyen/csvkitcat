#!/usr/bin/env python
# -*- coding: utf-8 -*-

import six
from subprocess import Popen, PIPE
import sys


try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

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

    def test_newline_handling(self):
        """newlines are stripped, including leading/trailing striplines"""
        self.assertLines(
            ["examples/linebreaks.csv",],
            ["fieldname,value", "id,1", "speech,hey", ",you", ",folks", ",whats up? ",],
        )

    def test_skip_lines(self):
        self.assertLines(
            ["--skip-lines", "3", "-D", "|", "examples/test_skip_lines.csv"],
            ["fieldname|value", "a|1", "b|2", "c|3",],
        )

    def test_forced_quoting_in_X_mode(self):
        self.assertLines(
            ["examples/dummy.csv", "-X", "42", "-U", "3"],
            ['"fieldname","value"', '"a","1"', '"b","2"', '"c","3"',],
        )

    ## X-chop
    def test_x_chop(self):
        self.assertLines(
            ["examples/statecodes.csv", "-X", "5"],
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
            ["examples/statecodes.csv", "-X", "5", "--chop-labels"],
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
            ["examples/tinyvals.csv", "--eor", "none"],
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
            ["examples/tinyvals.csv", "--eor", "False"],
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
        p1 = Popen(["csvflatten", "-X", "20", "examples/hamlet.csv"], stdout=PIPE)
        p2 = Popen(["csvlook"], stdin=p1.stdout, stdout=PIPE)
        p1.stdout.close()
        p1.wait()
        txt = p2.communicate()[0].decode("utf-8")
        p2.wait()

        assert (
            txt.splitlines()[-12:]
            == """
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
| lines     | Know you the hand?   |""".strip().splitlines()
        )

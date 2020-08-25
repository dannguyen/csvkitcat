#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import six

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

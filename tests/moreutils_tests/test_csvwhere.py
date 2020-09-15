#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

# import six

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from csvkitcat.moreutils.csvwhere import CSVWhere, launch_new_instance
from unittest import skip as skiptest

from tests.utils import (
    CSVKitTestCase,
    EmptyFileTests,
    # stdin_as_string,
)

from csvkitcat.exceptions import *


# TODO: EmptyFileTests


class TestCSVWhere(CSVKitTestCase):
    Utility = CSVWhere
    default_args = ["a,c", ">2"]

    def test_launch_new_instance(self):
        with patch.object(
            sys,
            "argv",
            [self.Utility.__name__.lower(), *self.default_args, "examples/dummy.csv"],
        ):
            launch_new_instance()

    def test_single(self):
        self.assertLines(
            ["age", ">40", "examples/peeps2.csv"],
            ["name,race,gender,age", "Dobbie,latino,male,50", "Furie,asian,female,60",],
        )

    def test_between_condition(self):
        self.assertLines(
            ["age", ">=40", "-A", "< 60", "examples/peeps2.csv"],
            [
                "name,race,gender,age",
                "Alice,white,female,40",
                "Dobbie,latino,male,50",
                "Ellie-Essie,black,female,40",
            ],
        )

    def test_between_condition_explicit(self):
        self.assertLines(
            ["age", ">=40", "--and", "age", "< 60", "examples/peeps2.csv"],
            [
                "name,race,gender,age",
                "Alice,white,female,40",
                "Dobbie,latino,male,50",
                "Ellie-Essie,black,female,40",
            ],
        )

    def test_between_plus_or_condition(self):
        self.assertLines(
            [
                "age",
                ">=40",
                "--and",
                "< 60",
                "--or",
                "name",
                "< D",
                "examples/peeps2.csv",
            ],
            [
                "name,race,gender,age",
                "Alice,white,female,40",
                "Bob,asian,male,30",
                "Callie,black,female,30",
                "Dobbie,latino,male,50",
                "Ellie-Essie,black,female,40",
            ],
        )

    skiptest("TODO")

    def test_datatype_specify_datetime(self):
        pass

    skiptest("TODO")

    def test_datatype_specify_number(self):
        pass

    skiptest("TODO")

    def test_when_datatype_clashes_with_agate_column_datatypes(self):
        pass

    skiptest("TODO")

    def test_when_additional_ops_swallows_input_file(self):
        pass


# peeps2
# [
#     "name,race,gender,age",
#     "Alice,white,female,40",
#     "Bob,asian,male,30",
#     "Callie,black,female,30",
#     "Dobbie,latino,male,50",
#     "Ellie-Essie,black,female,40",
#     "Furie,asian,female,60",
# ],

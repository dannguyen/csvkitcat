#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import six

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch


from csvkitcat.agatable import Aggregates
from csvkitcat.moreutils.csvgroupby import CSVGroupby, launch_new_instance
from csvkitcat.exceptions import *
from unittest import skip as skiptest

from tests.utils import (
    CSVKitTestCase,
    EmptyFileTests,
    stdin_as_string,
)

# TODO: EmptyFileTests


class TestCSVGroupby(CSVKitTestCase):
    Utility = CSVGroupby
    default_args = ["-c", "1"]

    def test_launch_new_instance(self):
        with patch.object(
            sys,
            "argv",
            [self.Utility.__name__.lower(), *self.default_args, "examples/dummy.csv"],
        ):
            launch_new_instance()

    def test_group_count(self):
        """same as csvpivot"""
        self.assertRows(
            ["-c", "gender", "examples/peeps.csv"],
            [["gender", "Count"], ["female", "4"], ["male", "2"],],
        )


    def test_group_count_multi_cols(self):
        """same as csvpivot"""
        self.assertRows(
            ["-c", "gender,race", "examples/peeps.csv"],
            [
                ["gender", "race", "Count"],
                ["female", "white", "1"],
                ["female", "black", "2"],
                ["female", "asian", "1"],
                ["male", "asian", "1"],
                ["male", "latino", "1"],
            ],
        )

    def test_group_count_named(self):
        """same as csvpivot"""
        self.assertRows(
            ["-c", "gender", "-a", "count:name", "examples/peeps.csv"],
            [["gender", "Count_of_name"], ["female", "4"], ["male", "2"],],
        )


    def test_group_sum(self):
        """similar as csvpivot"""
        self.assertRows(
            ["-c", "gender", "-a", "sum:age", "examples/peeps.csv"],
            [["gender", "Sum_of_age"], ["female", "90"], ["male", "45"],],
        )




    def test_print_list_of_aggs(self):
        self.assertLines(
            ["-a", "list", "examples/dummy.csv"],
            ["List of aggregate functions:"]
            + [f"- {a.__name__.lower()}" for a in Aggregates],
        )

    # #################################
    # ### Tests that verify my examples

    # """
    # name,race,gender,age
    # Joe,white,female,20
    # Jane,asian,male,20
    # Jill,black,female,20
    # Jim,latino,male,25
    # Julia,black,female,25
    # Joan,asian,female,25
    # """

    def test_examples_count_and_mean(self):
        self.assertLines(
            ["-c", "gender,race", '-a', 'count', '-a', 'mean:age', "examples/peeps.csv"],
            [
"gender,race,Count,Mean_of_age",
"female,white,1,20",
"female,black,2,22.5",
"female,asian,1,25",
"male,asian,1,20",
"male,latino,1,25",
],
        )




    ###############################
    ## error testing

    def test_error_when_no_columns(self):
        with self.assertRaises(ArgumentErrorTK) as e:
            u = self.get_output(["examples/dummy4.csv"])
        self.assertIn(
            "At least one column must be specified", str(e.exception)
        )

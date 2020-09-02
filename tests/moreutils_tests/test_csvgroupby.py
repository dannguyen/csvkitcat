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

    def test_group_count_column_matches(self):
        self.assertRows(
            ["-c", "name", "-a", 'count:greet,"hey, you"', "examples/greets.csv"],
            [
                ["name", "Count_of_greet_hey_you"],
                ["Alice", "1"],
                ["Bob", "2"],
                ["Cal", "0"],
                ["Dan", "0"],
            ],
        )

    def test_group_sum(self):
        """similar as csvpivot"""
        self.assertRows(
            ["-c", "gender", "-a", "sum:age", "examples/peeps.csv"],
            [["gender", "Sum_of_age"], ["female", "90"], ["male", "45"],],
        )

    def test_custom_column_names(self):
        self.assertLines(
            [
                "-c",
                "gender",
                "-a",
                "The Count|count",
                "-a",
                "Total Ages|sum:age",
                "-a",
                "Average Age|mean:age",
                "examples/peeps.csv",
            ],
            [
                "gender,The Count,Total Ages,Average Age",
                "female,4,90,22.5",
                "male,2,45,22.5",
            ],
        )

    # peeps2.csv
    # name,race,gender,age
    # Alice,white,female,40
    # Bob,asian,male,30
    # Callie,black,female,30
    # Dobbie,latino,male,50
    # Ellie-Essie,black,female,40
    # Furie,asian,female,60
    # Aggregates = (Count, Max, MaxLength, Min, Mean, Median, Mode, StDev, Sum)

    def test_all_aggs(self):
        self.assertRows(
            [
                "-c",
                "gender",
                "-a",
                "count",
                "-a",
                "count:name,Bob",
                "-a",
                "max:age",
                "-a",
                "maxlength:name",
                "-a",
                "mean:age",
                "-a",
                "median:age",
                "-a",
                "min:age",
                "-a",
                "mode:age",
                "-a",
                "stdev:age",  # no stdev since it requires minimum argument length of 2
                "-a",
                "sum:age",
                "examples/peeps2.csv",
            ],
            [
                [
                    "gender",
                    "Count",
                    "Count_of_name_bob",
                    "Max_of_age",
                    "MaxLength_of_name",
                    "Mean_of_age",
                    "Median_of_age",
                    "Min_of_age",
                    "Mode_of_age",
                    "StDev_of_age",
                    "Sum_of_age",
                ],
                [
                    "female",
                    "4",
                    "0",
                    "60",
                    "11",
                    "42.5",
                    "40",
                    "30",
                    "40",
                    "12.58305739211791616206114134",
                    "170",
                ],
                [
                    "male",
                    "2",
                    "1",
                    "50",
                    "6",
                    "40",
                    "40",
                    "30",
                    "30",
                    "14.14213562373095048801688724",
                    "80",
                ],
            ],
        )

    def test_print_list_of_aggs(self):
        self.assertLines(
            ["-a", "list", "examples/dummy.csv"],
            ["List of aggregate functions:"]
            + [f"- {a.__name__.lower()}" for a in Aggregates],
        )

    # #################################
    # ### Tests that verify my examples
    def test_examples_count_and_mean(self):
        self.assertLines(
            [
                "-c",
                "gender,race",
                "-a",
                "count",
                "-a",
                "mean:age",
                "-a",
                "TOTAL age|sum:age",
                "examples/peeps.csv",
            ],
            [
                "gender,race,Count,Mean_of_age,TOTAL age",
                "female,white,1,20,20",
                "female,black,2,22.5,45",
                "female,asian,1,25,25",
                "male,asian,1,20,20",
                "male,latino,1,25,25",
            ],
        )

    ###############################
    ## error testing

    def test_error_when_no_columns(self):
        with self.assertRaises(ArgumentErrorTK) as e:
            u = self.get_output(["examples/dummy4.csv"])
        self.assertIn("At least one column must be specified", str(e.exception))

    def test_error_when_invalid_aggregation_specified(self):
        with self.assertRaises(InvalidAggregation) as e:
            u = self.get_output(["-c", "1", "-a", "just magic!", "examples/dummy4.csv"])
        self.assertIn(
            'Invalid aggregation: "just magic!". Call `-a/--agg list` to get a list of available aggregations',
            str(e.exception),
        )

    def test_error_when_aggregation_has_invalid_column_name(self):
        with self.assertRaises(ColumnIdentifierError) as e:
            u = self.get_output(["-c", "a", "--agg", "sum:WRONG", "examples/dummy.csv"])

        self.assertIn(
            f"Expected column name 'WRONG' to refer to a column for Sum aggregation, but did not find it in table's list of column names:",
            str(e.exception),
        )

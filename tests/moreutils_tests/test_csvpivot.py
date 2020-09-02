#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import six

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch


from csvkitcat.agatable import Aggregates

from csvkitcat.moreutils.csvpivot import CSVPivot, launch_new_instance
from csvkitcat.exceptions import *
from unittest import skip as skiptest

from tests.utils import (
    CSVKitTestCase,
    EmptyFileTests,
    stdin_as_string,
)

# TODO: EmptyFileTests


class TestCSVPivot(CSVKitTestCase):
    Utility = CSVPivot
    default_args = ["-r", "a"]

    def test_launch_new_instance(self):
        with patch.object(
            sys,
            "argv",
            [self.Utility.__name__.lower(), "-r", "a", "examples/dummy.csv"],
        ):
            launch_new_instance()

    def test_count_rows(self):

        self.assertRows(
            ["-r", "code", "examples/statecodes.csv"],
            [["code", "Count"], ["IA", "1"], ["RI", "1"], ["TN", "1"],],
        )

    def test_count_cols(self):
        self.assertRows(
            ["-c", "code", "examples/statecodes.csv"],
            [["IA", "RI", "TN"], ["1", "1", "1"]],
        )

    def test_count_rows_n_cols(self):
        self.assertRows(
            ["-c", "code", "-r", "name", "examples/statecodes.csv"],
            [
                ["name", "IA", "RI", "TN"],
                ["Iowa", "1", "0", "0"],
                ["Rhode Island", "0", "1", "0"],
                ["Tennessee", "0", "0", "1"],
            ],
        )

    ################################
    # test -r accepts multiple column names

    def test_count_multi_rows(self):
        self.assertRows(
            ["-r", "gender,race", "examples/peeps.csv"],
            [
                ["gender", "race", "Count"],
                ["female", "white", "1"],
                ["female", "black", "2"],
                ["female", "asian", "1"],
                ["male", "asian", "1"],
                ["male", "latino", "1"],
            ],
        )

    def test_count_multi_rows_and_col(self):
        self.assertLines(
            ["-r", "gender,race", "-c", "name", "examples/peeps.csv"],
            [
                "gender,race,Joe,Jill,Julia,Joan,Jane,Jim",
                "female,white,1,0,0,0,0,0",
                "female,black,0,1,1,0,0,0",
                "female,asian,0,0,0,1,0,0",
                "male,asian,0,0,0,0,1,0",
                "male,latino,0,0,0,0,0,1",
            ],
        )

    ########################################
    # test -a/--agg aggregations
    # Count, Max, MaxLength, Min, Mean, Median, Mode, StDev, Sum

    def test_print_list_of_aggs(self):
        self.assertLines(
            ["-a", "list", "examples/dummy.csv"],
            ["List of aggregate functions:"]
            + [f"- {a.__name__.lower()}" for a in Aggregates],
        )

    def test_explicit_aggregation_of_count(self):
        """count is the default aggregate method, but we can also explicitly specify it"""
        self.assertRows(
            ["-r", "gender", "examples/peeps.csv"],
            [["gender", "Count"], ["female", "4"], ["male", "2"],],
        )

    def test_agg_sum(self):
        self.assertRows(
            ["-r", "gender", "-a", "sum:age", "examples/peeps.csv"],
            [["gender", "Sum"], ["female", "90"], ["male", "45"],],
        )

    # peeps2.csv
    # name,race,gender,age
    # Alice,white,female,40
    # Bob,asian,male,30
    # Callie,black,female,30
    # Dobbie,latino,male,50
    # Ellie-Essie,black,female,40
    # Furie,asian,female,60

    def test_agg_max(self):
        self.assertRows(
            ["-r", "race", "-a", "max:age", "examples/peeps2.csv"],
            [
                ["race", "Max"],
                ["white", "40"],
                ["asian", "60"],
                ["black", "40"],
                ["latino", "50"],
            ],
        )

    def test_agg_mean(self):
        self.assertRows(
            ["-r", "gender", "-a", "mean:age", "examples/peeps2.csv"],
            [["gender", "Mean"], ["female", "42.5"], ["male", "40"],],
        )

    def test_agg_median(self):
        self.assertRows(
            ["-r", "gender", "-a", "median:age", "examples/peeps2.csv"],
            [["gender", "Median"], ["female", "40"], ["male", "40"],],
        )

    def test_agg_mode(self):
        self.assertRows(
            ["-r", "gender", "-a", "mode:age", "examples/peeps2.csv"],
            [["gender", "Mode"], ["female", "40"], ["male", "30"],],
        )

    def test_agg_min(self):
        self.assertRows(
            ["-r", "race", "-a", "min:age", "examples/peeps2.csv"],
            [
                ["race", "Min"],
                ["white", "40"],
                ["asian", "30"],
                ["black", "30"],
                ["latino", "50"],
            ],
        )

    def test_agg_max_length(self):
        self.assertRows(
            ["-r", "race", "-a", "maxlength:name", "examples/peeps2.csv"],
            [
                ["race", "MaxLength"],
                ["white", "5"],
                ["asian", "5"],
                ["black", "11"],
                ["latino", "6"],
            ],
        )

    def test_agg_stdev(self):
        self.assertRows(
            ["-r", "gender", "-a", "stdev:age", "examples/peeps2.csv"],
            [
                ["gender", "StDev"],
                ["female", "12.58305739211791616206114134"],
                ["male", "14.14213562373095048801688724"],
            ],
        )

    # p-items.csv
    #
    # name,items
    # Alice,5
    # Bob,2
    # Chaz,
    # Bob,1
    # Alice,
    # Alice,7
    @skiptest(
        "cannot escape ValueError: https://github.com/wireservice/agate/issues/714"
    )
    def test_agg_max_w_null_col(self):
        self.assertRows(
            ["-r", "name", "-a", "max:items", "examples/p-items.csv"],
            [["name", "Max"], ["Alice", "7"], ["Bob", "2"], ["Chaz", ""],],
        )

    ########################################
    # test -a count,col_name,col_val

    def test_agg_count_non_nulls(self):
        self.assertRows(
            ["-r", "name", "-a", "count:items", "examples/p-items.csv"],
            [["name", "Count"], ["Alice", "2"], ["Bob", "2"], ["Chaz", "0"],],
        )

    def test_agg_count_value_matches(self):
        self.assertRows(
            ["-r", "name", "-a", 'count:greet,"hey, you"', "examples/greets.csv"],
            [
                ["name", "Count"],
                ["Alice", "1"],
                ["Bob", "2"],
                ["Cal", "0"],
                ["Dan", "0"],
            ],
        )

    #################################
    ### Tests that verify my examples

    """
    name,race,gender,age
    Joe,white,female,20
    Jane,asian,male,20
    Jill,black,female,20
    Jim,latino,male,25
    Julia,black,female,25
    Joan,asian,female,25
    """

    def test_examples_count_rows(self):
        self.assertRows(
            ["-r", "race", "examples/peeps.csv"],
            [
                ["race", "Count"],
                ["white", "1"],
                ["asian", "2"],
                ["black", "2"],
                ["latino", "1"],
            ],
        )

    def test_examples_count_multi_rows(self):
        self.assertLines(
            ["-r", "race,gender", "examples/peeps.csv"],
            [
                "race,gender,Count",
                "white,female,1",
                "asian,male,1",
                "asian,female,1",
                "black,female,2",
                "latino,male,1",
            ],
        )

    def test_examples_count_cols(self):
        self.assertRows(
            ["-c", "gender", "examples/peeps.csv"], [["female", "male"], ["4", "2"],]
        )

    def test_examples_count_rows_n_cols(self):
        self.assertRows(
            ["-r", "race", "-c", "gender", "examples/peeps.csv"],
            [
                ["race", "female", "male",],
                ["white", "1", "0",],
                ["asian", "1", "1",],
                ["black", "2", "0",],
                ["latino", "0", "1",],
            ],
        )

    ###############################
    ## error testing

    def test_error_when_no_row_or_column(self):
        with self.assertRaises(ArgumentErrorTK) as e:
            u = self.get_output(["examples/dummy4.csv"])
        assert (
            "At least either --row-pivot or --column-pivot must be specified. Both cannot be empty"
            in str(e.exception)
        )

    def test_error_when_pivot_column_has_multiple_cols(self):
        with self.assertRaises(ArgumentErrorTK) as e:
            u = self.get_output(["-c", "a,b", "examples/dummy4.csv"])
        assert "Only one --pivot-column is allowed, not 2:" in str(e.exception)

    def test_error_when_invalid_aggregation_specified(self):
        with self.assertRaises(InvalidAggregation) as e:
            u = self.get_output(["-c", "b", "-a", "just magic!", "examples/dummy4.csv"])
        self.assertIn(
            'Invalid aggregation: "just magic!". Call `-a/--agg list` to get a list of available aggregations',
            str(e.exception),
        )

    def test_error_when_aggregating_on_null_column(self):
        with self.assertRaises(ValueError) as e:
            u = self.get_output(
                ["-r", "name", "-a", "max:items", "examples/p-items.csv"]
            )
        assert "max() arg is an empty sequence" in str(e.exception)

    def test_error_when_aggregating_non_numer_column(self):
        with self.assertRaises(DataTypeError) as e:
            u = self.get_output(
                ["-r", "gender", "--agg", "sum:name", "examples/peeps.csv"]
            )

        assert "Sum can only be applied to columns containing Number data" in str(
            e.exception
        )

    def test_error_when_aggregation_has_invalid_column_name(self):
        with self.assertRaises(ColumnIdentifierError) as e:
            u = self.get_output(["-c", "a", "--agg", "sum:WRONG", "examples/dummy.csv"])

        self.assertIn(
            f"Expected column name 'WRONG' to refer to a column for Sum aggregation, but did not find it in table's list of column names:",
            str(e.exception),
        )

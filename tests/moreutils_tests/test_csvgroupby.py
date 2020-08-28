#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import six

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch


from csvkitcat.moreutils.csvgroupby import CSVGroupby, GroupbyAggs, launch_new_instance
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

    @skiptest('TODO')
    def test_examples_count_and_sum(self):
        self.assertLines(
            ["-c", "race,gender", '-a', 'count', '-a', 'sum,age' "examples/peeps.csv"],
            [
                "race,gender,Count,Sum_age",
                "white,female,1,20",
                "asian,male,1,20",
                "asian,female,1,25",
                "black,female,2,45",
                "latino,male,1,25",
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

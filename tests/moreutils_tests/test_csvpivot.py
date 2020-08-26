#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import six

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from csvkitcat.moreutils.csvpivot import CSVPivot, launch_new_instance
from tests.utils import (
    CSVKitTestCase,
    EmptyFileTests,
    stdin_as_string,
)

# TODO: EmptyFileTests

class TestCSVPivot(CSVKitTestCase):
    Utility = CSVPivot
    default_args = ['-r', 'a']

    def test_launch_new_instance(self):
        with patch.object(
            sys, "argv", [self.Utility.__name__.lower(), '-r', 'a', "examples/dummy.csv"]
        ):
            launch_new_instance()

    def test_count_rows(self):

        self.assertRows(['-r', 'code', "examples/statecodes.csv"], [
            ['code', 'Count'],
            ['IA', '1'],
            ['RI', '1'],
            ['TN', '1'],]
        )


    def test_count_cols(self):
        self.assertRows(['-c', 'code', "examples/statecodes.csv"], [
            ['IA', 'RI', 'TN'],
            ['1', '1', '1']
        ])

    def test_count_rows_n_cols(self):
        self.assertRows(['-c', 'code', '-r', 'name', "examples/statecodes.csv"], [
            ['name',         'IA', 'RI', 'TN'],
            ['Iowa',         '1',  '0',  '0'],
            ['Rhode Island', '0',  '1',  '0'],
            ['Tennessee',    '0',  '0',  '1'],

        ])




#################################
### Tests that verify my examples

    def test_examples_count_rows(self):
        self.assertRows(['-r', 'race', "examples/peeps.csv"], [
            ['race',    'Count'],
            ['white',    '1'],
            ['asian',    '2'],
            ['black',    '2'],
            ['latino',   '1'],
            ]
        )


    def test_examples_count_cols(self):
        self.assertRows(['-c', 'gender', "examples/peeps.csv"], [
            ['female', 'male'],
            ['4',       '2'],
        ])


    def test_examples_count_rows_n_cols(self):
        self.assertRows(['-r', 'race', '-c', 'gender', "examples/peeps.csv"], [
            ['race',   'female', 'male', ],
            ['white',    '1',     '0', ],
            ['asian',    '1',     '1', ],
            ['black',    '2',     '0', ],
            ['latino',   '0',     '1', ],
            ]
        )

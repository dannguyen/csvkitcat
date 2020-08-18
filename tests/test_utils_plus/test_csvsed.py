#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import six

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from csvkit.exceptions import ColumnIdentifierError
from csvkitcat.utils_plus.csvsed import CSVSed,  launch_new_instance
from tests.utils import CSVKitTestCase, stdin_as_string, EmptyFileTests



class TestCSVFlatten(CSVKitTestCase, EmptyFileTests):
    Utility = CSVSed
    default_args = ['hello', 'world']

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', [self.Utility.__name__.lower(), 'hey', 'you', 'examples/dummy.csv']):
            launch_new_instance()


    def test_basic_dummy(self):
        """
        Shouldn't alter headers
        """
        self.assertLines([r'(\w)', r'\1!', 'examples/dummy.csv' ], [
            "a,b,c",
            "1!,2!,3!",
        ])


    def test_outputs_non_pattern_matches_too(self):
        self.assertLines([r'([a-z])', r'\1!',
                         'examples/tinyvals.csv'],

            ["alpha,omega",
            "1,9",
            "a!,z!",
            "$,%",])


    def test_column_choice(self):
        self.assertLines(['-c', 'b,c',
                        r'(\w)', r'\1!',
                        'examples/dummy.csv' ], [
            "a,b,c",
            "1,2!,3!",
        ])

    def test_supports_case_insensitivity(self):
        self.assertLines([r'(?i)miss', 'Ms.',
                        'examples/honorifics-fem.csv' ], [
            "code,name",
            "1,Mrs. Smith",
            "2,Ms. Daisy",
            "3,Ms. Doe",
            "4,Mrs Miller",
            "5,Ms Lee",
            "6,Ms. maam",
        ])


    def test_literal_match(self):
        self.assertLines(['-m',
                        's.', 'x.',
                        'examples/honorifics-fem.csv' ], [
            "code,name",
            "1,Mrx. Smith",
            "2,Miss Daisy",
            "3,Mx. Doe",
            "4,Mrs Miller",
            "5,Ms Lee",
            "6,miss maam",
        ])


    def test_hacky_strip(self):
        self.assertLines([  r'^\s*(.+?)\s*$', r'\1',
                            'examples/consec_ws.csv'], [
            "id,phrase",
            "1,hello world",
            "2,good   bye",
            "3,a  ok",
        ])

# class ColumnsTests(object):
    def test_invalid_column(self):
        args = ['-c', '0',] + self.default_args + ['examples/dummy.csv']

        output_file = six.StringIO()
        utility = self.Utility(args, output_file)

        with self.assertRaises(ColumnIdentifierError):
            utility.run()

        output_file.close()


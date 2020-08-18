#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import six

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from csvkitcat.utils_plus.csvsqueeze import CSVSqueeze, launch_new_instance
from tests.utils import CSVKitTestCase, EmptyFileTests, stdin_as_string, ColumnsTests, NamesTests



class TestCSVFormat(CSVKitTestCase, EmptyFileTests):
    Utility = CSVSqueeze

    def test_launch_new_instance(self):
        with patch.object(sys, 'argv', [self.Utility.__name__.lower(), 'examples/dummy.csv']):
            launch_new_instance()


    def test_basic_dummy(self):
        """
        Shouldn't alter a file with no whitespace/nonprintable characters whatsoever
        """
        self.assertLines(['examples/dummy.csv'], [
            "a,b,c",
            "1,2,3",
        ])


    def test_default_squeeze(self):
        """
        squeeze with all the works
        """
        self.assertLines(['examples/mess.csv'], [
            "code,name",
            "1,Dan",
            "0 2,Billy Bob",
            "0003,..Who..?",
            "4,Mr. R obot",
        ])

    def test_squeeze_does_not_affect_headers(self):
          self.assertLines(['examples/mess_head.csv', '-u', '0'], [
            ''' code   ," the  first''',
            ''' name   "''',
            "1,Dan",
            "0 2,Billy Bob",
        ])


    def test_keep_consecutive_whitespace(self):
        self.assertLines(['examples/consec_ws.csv', '--keep-consecutive-ws'], [
            "id,phrase",
            "1,hello world",
            "2,good   bye",
            "3,a  ok"
        ])


    def test_kill_lines(self):
        self.assertLines(['examples/linebreaks.csv',], [
            "id,speech",
            '''1,hey you folks whats up?''',
        ])

    def test_keep_lines(self):
        self.assertLines(['examples/linebreaks.csv', '--keep-lines'], [
            "id,speech",
            '''1,"hey''',
            'you','folks','whats up?"',
        ])


######## test column choice
    def test_selected_columns_squeezed(self):
        self.assertLines(['examples/consec_ws.csv', '-c', 'id'], [
            "id,phrase",
            "1,hello world",
            "2,good   bye",
            "3,  a  ok",
        ])

    def test_selected_columns_squeezed_w_options(self):
        """since Column 1 is not selected, no stripping of `id` is done"""

        self.assertLines(['examples/consec_ws.csv', '-c', '2', '--keep-consecutive-ws'], [
            "id,phrase",
            "1,hello world",
            "2,good   bye",
            " 3  ,a  ok"
        ])


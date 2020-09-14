import unittest
from unittest import skip as skiptest

import csvkitcat
import csvkitcat.__about__ as about


class FunTestCase(unittest.TestCase):
    def test_about(self):
        self.assertEqual("csvkitcat", about.__title__)

    def test_version(self):
        self.assertIn("alpha", about.__version__)

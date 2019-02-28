#!/usr/bin/env python3

import unittest
from KaSaAn.core import KappaCounter


class TestKappaCounter(unittest.TestCase):
    """Test various elements of a KappaCounter representation."""
    def test_string_representation(self):
        self.assertEqual(str(KappaCounter('c{ = 5}')), 'c{=5}')
        self.assertEqual(str(KappaCounter('~c{ = 5 / += 3}')), '~c{=5/+=3}')
        self.assertEqual(str(KappaCounter('_1{ = 5 / -= 3}')), '_1{=5/-=3}')

    def test_get_counter_name(self):
        self.assertEqual(KappaCounter('c1{=11}').get_counter_name(), 'c1')
        self.assertEqual(KappaCounter('~a{=11}').get_counter_name(), '~a')
        self.assertEqual(KappaCounter('_b{=11}').get_counter_name(), '_b')

    def test_get_counter_state(self):
        self.assertEqual(KappaCounter('c1{=11}').get_counter_state(), '=11')
        self.assertEqual(KappaCounter('c1{>=11}').get_counter_state(), '>=11')
        self.assertEqual(KappaCounter('c1{=11/+=99}').get_counter_state(), '=11/+=99')

    def test_get_counter_tested_value(self):
        self.assertEqual(KappaCounter('c1{=11/+=99}').get_counter_tested_value(), '=11')
        self.assertEqual(KappaCounter('c1{>=11/+=99}').get_counter_tested_value(), '>=11')

    def test_get_counter_delta(self):
        self.assertEqual(KappaCounter('c1{=11/-=99}').get_counter_delta(), '-=99')
        self.assertEqual(KappaCounter('c1{>=11/+=99}').get_counter_delta(), '+=99')

    def test_has_operation(self):
        self.assertFalse(KappaCounter('c1{>=11}').has_operation())
        self.assertFalse(KappaCounter('c1{=11}').has_operation())
        self.assertTrue(KappaCounter('c1{>=11/+=99}').has_operation())

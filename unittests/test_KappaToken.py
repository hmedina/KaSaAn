#!/usr/bin/env python3

import unittest
from KaSaAn.core import KappaToken


class TestKappaToken(unittest.TestCase):
    """Test various elements of KappaToken representation."""
    def test_string_representation(self):
        self.assertEqual(str(KappaToken('bob')), 'bob')
        self.assertEqual(str(KappaToken('~a')), '~a')
        self.assertEqual(str(KappaToken('_1')), '_1')
        self.assertEqual(str(KappaToken('55 jane')), '55 jane')
        self.assertEqual(str(KappaToken('+9 jane')), '+9 jane')
        self.assertEqual(str(KappaToken('-9 jane')), '-9 jane')

    def test_get_token_name(self):
        self.assertEqual(KappaToken('99 bob').get_token_name(), 'bob')
        self.assertEqual(KappaToken('99 _d').get_token_name(), '_d')

    def test_get_token_operation(self):
        self.assertEqual(KappaToken('+99 ATP').get_token_operation(), '+99')
        self.assertEqual(KappaToken('-99 ATP').get_token_operation(), '-99')
        self.assertEqual(KappaToken('99 ATP').get_token_operation(), '99')

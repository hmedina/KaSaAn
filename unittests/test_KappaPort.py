#!/usr/bin/env python3

import unittest
from KaSaAn.core import KappaPort


class TestKappaPort(unittest.TestCase):
    """Test various elements of a KappaPort representation."""
    def test_string_representation(self):
        self.assertEqual(str(KappaPort('~a')), '~a[#]{#}')
        self.assertEqual(str(KappaPort('~a[#]{#}')), '~a[#]{#}')
        self.assertEqual(str(KappaPort('~a{#}[#]')), '~a[#]{#}')

    def test_get_port_name(self):
        self.assertEqual(KappaPort('bob').get_port_name(), 'bob')
        self.assertEqual(KappaPort('bob[.]').get_port_name(), 'bob')
        self.assertEqual(KappaPort('bob{p}').get_port_name(), 'bob')
        self.assertEqual(KappaPort('bob{p}[_]').get_port_name(), 'bob')

    def test_get_port_int_state(self):
        self.assertEqual(KappaPort('bob{ph}').get_port_int_state(), 'ph')
        self.assertEqual(KappaPort('bob').get_port_int_state(), '#')
        self.assertEqual(KappaPort('bob[.]{ph}').get_port_int_state(), 'ph')
        self.assertEqual(KappaPort('bob{ph}[.]').get_port_int_state(), 'ph')
        self.assertEqual(KappaPort('bob{ph/un}[.]').get_port_int_state(), 'ph/un')

    def test_get_port_bond_state(self):
        self.assertEqual(KappaPort('_b[1]').get_port_bond_state(), '1')
        self.assertEqual(KappaPort('_b[_]').get_port_bond_state(), '_')
        self.assertEqual(KappaPort('_b[#]').get_port_bond_state(), '#')
        self.assertEqual(KappaPort('_b').get_port_bond_state(), '#')
        self.assertEqual(KappaPort('_b[.]{ph}').get_port_bond_state(), '.')
        self.assertEqual(KappaPort('_b{ph}[.]').get_port_bond_state(), '.')
        self.assertEqual(KappaPort('_b[./1]{ph}').get_port_bond_state(), './1')

    def test_get_port_current_bond(self):
        self.assertEqual(KappaPort('_b[./1]{ph}').get_port_current_bond(), '.')
        self.assertEqual(KappaPort('_b[55/99]{ph}').get_port_current_bond(), '55')
        self.assertEqual(KappaPort('_b[99]{ph}').get_port_current_bond(), '99')

    def test_get_port_future_bond(self):
        self.assertEqual(KappaPort('_b[./1]{ph}').get_port_future_bond(), '1')
        self.assertEqual(KappaPort('_b[99/1]{ph}').get_port_future_bond(), '1')
        self.assertEqual(KappaPort('_b[99/.]{ph}').get_port_future_bond(), '.')
        self.assertEqual(KappaPort('_b[99]{ph}').get_port_future_bond(), '')

    def test_get_port_current_state(self):
        self.assertEqual(KappaPort('bob{ph/un}[.]').get_port_current_state(), 'ph')
        self.assertEqual(KappaPort('bob{ph+/un-}[.]').get_port_current_state(), 'ph+')
        self.assertEqual(KappaPort('bob{un}[.]').get_port_current_state(), 'un')

    def test_get_port_future_state(self):
        self.assertEqual(KappaPort('bob{ph/un}[.]').get_port_future_state(), 'un')
        self.assertEqual(KappaPort('bob{ph+/un-}[.]').get_port_future_state(), 'un-')
        self.assertEqual(KappaPort('bob{gh}[.]').get_port_future_state(), '')

    def test_get_port_bond_operation(self):
        self.assertEqual(KappaPort('jane[./1]').get_port_bond_operation(), 'creation')
        self.assertEqual(KappaPort('jane[1/.]').get_port_bond_operation(), 'deletion')
        self.assertEqual(KappaPort('jane[1/2]').get_port_bond_operation(), 'swap')
        self.assertEqual(KappaPort('jane[2]').get_port_bond_operation(), '')

    def test_has_bond_operation(self):
        self.assertTrue(KappaPort('_b[./1]{ph/un}').has_bond_operation())
        self.assertFalse(KappaPort('_b[1]{ph/un}').has_bond_operation())

    def test_has_state_operation(self):
        self.assertTrue(KappaPort('~a{un/ph}[1/2]').has_state_operation())
        self.assertFalse(KappaPort('~a{ph}[2/.]').has_state_operation())

    def test_inclusion_criteria(self):
        self.assertTrue('a[1]' in KappaPort('a[1]{s}'))
        self.assertTrue('a[_]' in KappaPort('a[1]{s}'))
        self.assertTrue('a[.]' in KappaPort('a[.]{s}'))
        self.assertTrue('a{s}' in KappaPort('a[1]{s}'))
        self.assertTrue('a{#}' in KappaPort('a[1]{s}'))
        self.assertTrue('a{s}' in KappaPort('a[1]{#}'))
        self.assertTrue('a[1]' in KappaPort('a[_]{#}'))
        self.assertTrue('a[1]' in KappaPort('a[#]{#}'))
        self.assertTrue('a[1]' in KappaPort('a[1]'))
        self.assertFalse('a[.]' in KappaPort('a[1]{s}'))
        self.assertFalse('a[_]' in KappaPort('a[.]{s}'))
        self.assertFalse('a{u}' in KappaPort('a[1]{s}'))

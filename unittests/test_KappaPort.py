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

    def test_satisfaction_port_name(self):
        self.assertTrue('site' in KappaPort('site'))
        self.assertFalse('site' in KappaPort('other_site'))

    def test_satisfaction_internal_state(self):
        self.assertTrue('site{#}' in KappaPort('site{#}'))
        self.assertFalse('site{a}' in KappaPort('site{#}'))

        self.assertTrue('site{#}' in KappaPort('site{b}'))
        self.assertTrue('site{b}' in KappaPort('site{b}'))

        self.assertFalse('site{c}' in KappaPort('site{d}'))

    def test_satisfaction_bond_state(self):
        self.assertTrue('site[#]' in KappaPort('site[#]'))
        self.assertFalse('site[_]' in KappaPort('site[#]'))
        self.assertFalse('site[.]' in KappaPort('site[#]'))
        self.assertFalse('site[8]' in KappaPort('site[#]'))

        self.assertTrue('site[#]' in KappaPort('site[_]'))
        self.assertTrue('site[_]' in KappaPort('site[_]'))
        self.assertFalse('site[.]' in KappaPort('site[_]'))
        self.assertFalse('site[7]' in KappaPort('site[_]'))

        self.assertTrue('site[#]' in KappaPort('site[.]'))
        self.assertFalse('site[_]' in KappaPort('site[.]'))
        self.assertTrue('site[.]' in KappaPort('site[.]'))
        self.assertFalse('site[6]' in KappaPort('site[.]'))

        self.assertTrue('site[#]' in KappaPort('site[5]'))
        self.assertTrue('site[_]' in KappaPort('site[5]'))
        self.assertFalse('site[.]' in KappaPort('site[5]'))
        self.assertTrue('site[5]' in KappaPort('site[5]'))

        self.assertFalse('site[4]' in KappaPort('site[3]'))

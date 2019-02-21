#!/usr/bin/env python3

import unittest
from KaSaAn import KappaPort, KappaCounter, KappaAgent, KappaToken, KappaComplex, KappaSnapshot, KappaRule


class TestKappaParse(unittest.TestCase):
    """Unit tests to check for broken or breaking parsing."""

    def test_port(self):
        # string representation
        self.assertEqual(str(KappaPort('~a')), '~a[#]{#}')          # name passed
        self.assertEqual(str(KappaPort('~a[#]{#}')), '~a[#]{#}')    # signature passed
        self.assertEqual(str(KappaPort('~a{#}[#]')), '~a[#]{#}')    # ordering of signature passed
        # parsing port's name
        self.assertEqual(KappaPort('bob').get_port_name(), 'bob')
        self.assertEqual(KappaPort('bob[.]').get_port_name(), 'bob')
        self.assertEqual(KappaPort('bob{p}').get_port_name(), 'bob')
        # parsing port's internal state
        self.assertEqual(KappaPort('bob{ph}').get_port_int_state(), 'ph')
        self.assertEqual(KappaPort('bob').get_port_int_state(), '#')
        self.assertEqual(KappaPort('bob[.]{ph}').get_port_int_state(), 'ph')
        self.assertEqual(KappaPort('bob{ph}[.]').get_port_int_state(), 'ph')
        self.assertEqual(KappaPort('bob{ph/un}[.]').get_port_int_state(), 'ph/un')
        self.assertEqual(KappaPort('bob{ph/un}[.]').get_port_current_state(), 'ph')
        self.assertEqual(KappaPort('bob{ph/un}[.]').get_port_future_state(), 'un')
        self.assertTrue(KappaPort('~a{un/ph}[1/2]').has_state_operation())
        self.assertFalse(KappaPort('~a{ph}[2]').has_state_operation())
        # parsing port's bond state
        self.assertEqual(KappaPort('_b[1]').get_port_bond_state(), '1')
        self.assertEqual(KappaPort('_b').get_port_bond_state(), '#')
        self.assertEqual(KappaPort('_b[.]{ph}').get_port_bond_state(), '.')
        self.assertEqual(KappaPort('_b{ph}[.]').get_port_bond_state(), '.')
        self.assertEqual(KappaPort('_b[./1]{ph}').get_port_bond_state(), './1')
        self.assertEqual(KappaPort('_b[./1]{ph}').get_port_current_bond(), '.')
        self.assertEqual(KappaPort('_b[./1]{ph}').get_port_future_bond(), '1')
        self.assertTrue(KappaPort('_b[./1]{ph}').has_bond_operation())
        self.assertFalse(KappaPort('_b[1]{ph}').has_bond_operation())


#    def test_counter(self):

#    def test_agent(self):

#    def test_token(self):

#    def test_complex(self):

#    def test_snapshot(self):

#    def test_rule(self):


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3

import unittest
from KaSaAn import KappaPort, KappaCounter, KappaAgent, KappaToken, KappaComplex, KappaSnapshot, KappaRule
#from ..core import KappaPort, KappaCounter, KappaAgent, KappaToken, KappaComplex, KappaSnapshot, KappaRule
# above line is just a hack to get PyCharm to load properly as it can't seem to read the PythonPath correctly


class TestKappaParse(unittest.TestCase):
    """Unit tests to check for broken or breaking parsing."""

    def test_port(self):
        # string representation
        self.assertEqual(str(KappaPort('~a')), '~a[#]{#}')
        self.assertEqual(str(KappaPort('~a[#]{#}')), '~a[#]{#}')
        self.assertEqual(str(KappaPort('~a{#}[#]')), '~a[#]{#}')
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
        # inclusion testing
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


    def test_counter(self):
        # string representation
        self.assertEqual(str(KappaCounter('c{ = 5}')), 'c{=5}')
        self.assertEqual(str(KappaCounter('~c{ = 5 / += 3}')), '~c{=5/+=3}')
        self.assertEqual(str(KappaCounter('_1{ = 5 / -= 3}')), '_1{=5/-=3}')
        # snapshot-like usage
        self.assertEqual(KappaCounter('c1{=11}').get_counter_name(),'c1')
        self.assertEqual(KappaCounter('c1{=11}').get_counter_state(), '=11')
        self.assertEqual(KappaCounter('c1{>=11}').get_counter_state(), '>=11')
        self.assertFalse(KappaCounter('c1{>=11}').has_operation())
        # rule usage (edit notation)
        self.assertEqual(KappaCounter('c1{=11/+=99}').get_counter_state(), '=11/+=99')
        self.assertEqual(KappaCounter('c1{=11/+=99}').get_counter_tested_value(), '=11')
        self.assertEqual(KappaCounter('c1{>=11/+=99}').get_counter_tested_value(), '>=11')
        self.assertEqual(KappaCounter('c1{>=11/+=99}').get_counter_delta(), '+=99')
        self.assertTrue(KappaCounter('c1{>=11/+=99}').has_operation())


#    def test_agent(self):

#    def test_token(self):

#    def test_complex(self):

#    def test_snapshot(self):

#    def test_rule(self):


if __name__ == '__main__':
    unittest.main()

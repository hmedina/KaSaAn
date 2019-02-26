#!/usr/bin/env python3

import unittest
from KaSaAn import KappaPort, KappaCounter, KappaAgent, KappaToken, KappaComplex, KappaSnapshot, KappaRule
#from ..core import KappaPort, KappaCounter, KappaAgent, KappaToken, KappaComplex, KappaSnapshot, KappaRule
# above line is just a hack to get PyCharm to load properly as it can't seem to read the PythonPath correctly


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


class TestKappaAgent(unittest.TestCase):
    """Test various elements of a KappaAgent representation."""
    def test_string_representation(self):
        self.assertEqual(str(KappaAgent('Bob()')), 'Bob()')
        self.assertEqual(str(KappaAgent('Bob(s1)')), 'Bob(s1[#]{#})')
        self.assertEqual(str(KappaAgent('Bob(s2, s1)')), 'Bob(s1[#]{#} s2[#]{#})')
        self.assertEqual(str(KappaAgent('Bob(s1[11]{ph})')), 'Bob(s1[11]{ph})')
        self.assertEqual(str(KappaAgent('Bob(s1{ph}[99])')), 'Bob(s1[99]{ph})')
        self.assertEqual(str(KappaAgent('_1()')), '_1()')
        self.assertEqual(str(KappaAgent('~a()')), '~a()')

    def test_inclusion_criteria(self):
        self.assertTrue('Bob()' in KappaAgent('Bob()'))
        self.assertTrue('s1[.]' in KappaAgent('Bob(s1[.])'))
        self.assertTrue('s1[_]' in KappaAgent('Bob(s1[11])'))
        self.assertFalse('s1[.]' in KappaAgent('Bob(s1[11])'))
        self.assertFalse('s1[_]' in KappaAgent('Bob(s1[.])'))
        self.assertTrue('s2{ph}' in KappaAgent('Bob(s1, s2{ph}[22])'))
        self.assertTrue('s2[11]' in KappaAgent('Bob(s1, s2{ph}[11])'))
        self.assertFalse('s2{ph}' in KappaAgent('Bob(s1, s2{un})'))
        self.assertTrue(KappaAgent('Bob(s1[.]{ph})') in KappaAgent('Bob(s1[.]{ph}, s2[11]{gh})'))
        self.assertTrue('s1[#]' in KappaAgent('Bob(s1[.]{ph}, s2[11]{gh})'))
        self.assertTrue('s1{#}' in KappaAgent('Bob(s1[.]{ph}, s2[11]{gh})'))
        self.assertFalse('s3[#]{#}' in KappaAgent('Bob(s1[.]{ph}, s2[11]{gh})'))

    def test_get_agent_name(self):
        self.assertEqual('Bob', KappaAgent('Bob(s1[_]{pd}, s2[.]{ds})').get_agent_name())
        self.assertEqual('~1', KappaAgent('~1(s1[_]{pd}, s2[.]{ds})').get_agent_name())
        self.assertEqual('_DD', KappaAgent('_DD(s1[_]{pd}, s2[.]{ds})').get_agent_name())

    def test_get_agent_signature(self):
        self.assertEqual('s1[_]{pd}', str(KappaAgent('Bob(s1{pd}[_], s2[.]{ds})').get_agent_signature()[0]))
        self.assertEqual('s2[.]{ds}', str(KappaAgent('Bob(s1{pd}[_], s2[.]{ds})').get_agent_signature()[1]))
        self.assertCountEqual([KappaPort('s1[3]{ph}'), KappaPort('_2'), KappaCounter('c3{=55}')],
                              KappaAgent('Jane(s1{ph}[3], _2, c3{=55})').get_agent_signature())

    def test_get_bond_identifiers(self):
        self.assertCountEqual(['1', '33', '999'], KappaAgent('Mary(~a[1], _b[33], cc[999])').get_bond_identifiers())

    def test_get_abundance_change_operation(self):
        self.assertEqual('+', KappaAgent('Mary(s-1[1]{ph-})+').get_abundance_change_operation())
        self.assertEqual('-', KappaAgent('Mary(s+1[1]{ph+})-').get_abundance_change_operation())
        self.assertEqual('', KappaAgent('Mary(s-1[1]{ph+})').get_abundance_change_operation())


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


class TestKappaComplex(unittest.TestCase):
    """Testing various elements of KappaComplex representation."""
    def test_string_representation(self):
        self.assertEqual(str(KappaComplex('_a(s1[1]), ~b(~a[1], bob[2]), bob(~b[2])')),
                         '_a(s1[1]{#}), bob(~b[2]{#}), ~b(bob[2]{#} ~a[1]{#})')

    def test_get_number_of_bonds(self):
        self.assertEqual(KappaComplex('_a(s1[1]{#}), bob(~b[2]{#}), ~b(bob[2]{#} ~a[1]{#})').get_number_of_bonds(), 2)

    def test_get_size_of_complex(self):
        self.assertEqual(KappaComplex('_a(s1[1]{#}), bob(~b[3]{#}), ~b(bob[2]{#} ~a[1]{#})').get_size_of_complex(), 3)
        self.assertEqual(KappaComplex(
            'Ah(a[.] b[.] c[1] d[.] e[.] f[.] g[.] h[.] i[.] j[.] k[.] l[.] m[.] n[.] o[.] p[.] q[.] r[.] s[.] t[.] u[.] v[.] w[.] x[.] y[.] z[.]),Ac(a[.] b[.] c[.] d[.] e[2] f[3] g[.] h[1] i[4] j[.] k[.] l[.] m[5] n[.] o[.] p[6] q[7] r[.] s[8] t[.] u[.] v[9] w[.] x[.] y[.] z[.]),Ae(a[.] b[.] c[2] d[.] e[.] f[.] g[.] h[.] i[.] j[.] k[.] l[.] m[.] n[.] o[.] p[.] q[.] r[.] s[.] t[.] u[.] v[.] w[.] x[.] y[.] z[.]),Af(a[.] b[.] c[3] d[.] e[.] f[.] g[.] h[.] i[.] j[.] k[.] l[.] m[.] n[.] o[.] p[.] q[.] r[.] s[.] t[.] u[.] v[.] w[.] x[.] y[.] z[.]),Ai(a[.] b[.] c[4] d[.] e[.] f[.] g[.] h[.] i[.] j[.] k[.] l[.] m[.] n[.] o[.] p[.] q[.] r[.] s[.] t[.] u[.] v[.] w[.] x[.] y[.] z[.]),Am(a[.] b[.] c[5] d[.] e[.] f[.] g[.] h[.] i[.] j[.] k[.] l[.] m[.] n[.] o[.] p[.] q[.] r[.] s[.] t[.] u[.] v[.] w[.] x[.] y[.] z[.]),Ap(a[.] b[.] c[6] d[.] e[.] f[.] g[.] h[.] i[.] j[.] k[.] l[.] m[.] n[.] o[.] p[.] q[.] r[.] s[.] t[.] u[.] v[.] w[.] x[.] y[.] z[.]),Aq(a[.] b[.] c[7] d[.] e[.] f[.] g[.] h[.] i[.] j[.] k[.] l[.] m[.] n[.] o[.] p[.] q[.] r[.] s[.] t[.] u[.] v[.] w[.] x[.] y[.] z[.]),As(a[.] b[.] c[8] d[.] e[.] f[.] g[.] h[.] i[.] j[.] k[.] l[.] m[.] n[.] o[.] p[.] q[.] r[.] s[.] t[.] u[.] v[.] w[.] x[.] y[.] z[.]),Av(a[.] b[.] c[9] d[.] e[.] f[.] g[.] h[.] i[.] j[.] k[.] l[.] m[.] n[.] o[.] p[.] q[.] r[.] s[.] t[.] u[.] v[.] w[.] x[.] y[.] z[.])').
                         get_size_of_complex(), 10)

    def test_get_agent_types(self):
        self.assertEqual(KappaComplex('_a(s1[1]{#}), bob(~b[3]{#}), ~b(bob[2]{#} ~a[1]{#})').get_agent_types(),
                         {KappaAgent('_a'), KappaAgent('~b'), KappaAgent('bob')})

    def test_get_all_agents(self):
        self.assertCountEqual(KappaComplex(
            'Ah(a[.] b[.] c[1] d[.] e[.] f[.] g[.] h[.] i[.] j[.] k[.] l[.] m[.] n[.] o[.] p[.] q[.] r[.] s[.] t[.] u[.] v[.] w[.] x[.] y[.] z[.]),Ac(a[.] b[.] c[.] d[.] e[2] f[3] g[.] h[1] i[4] j[.] k[.] l[.] m[5] n[.] o[.] p[6] q[7] r[.] s[8] t[.] u[.] v[9] w[.] x[.] y[.] z[.]),Ae(a[.] b[.] c[2] d[.] e[.] f[.] g[.] h[.] i[.] j[.] k[.] l[.] m[.] n[.] o[.] p[.] q[.] r[.] s[.] t[.] u[.] v[.] w[.] x[.] y[.] z[.]),Af(a[.] b[.] c[3] d[.] e[.] f[.] g[.] h[.] i[.] j[.] k[.] l[.] m[.] n[.] o[.] p[.] q[.] r[.] s[.] t[.] u[.] v[.] w[.] x[.] y[.] z[.]),Ai(a[.] b[.] c[4] d[.] e[.] f[.] g[.] h[.] i[.] j[.] k[.] l[.] m[.] n[.] o[.] p[.] q[.] r[.] s[.] t[.] u[.] v[.] w[.] x[.] y[.] z[.]),Am(a[.] b[.] c[5] d[.] e[.] f[.] g[.] h[.] i[.] j[.] k[.] l[.] m[.] n[.] o[.] p[.] q[.] r[.] s[.] t[.] u[.] v[.] w[.] x[.] y[.] z[.]),Ap(a[.] b[.] c[6] d[.] e[.] f[.] g[.] h[.] i[.] j[.] k[.] l[.] m[.] n[.] o[.] p[.] q[.] r[.] s[.] t[.] u[.] v[.] w[.] x[.] y[.] z[.]),Aq(a[.] b[.] c[7] d[.] e[.] f[.] g[.] h[.] i[.] j[.] k[.] l[.] m[.] n[.] o[.] p[.] q[.] r[.] s[.] t[.] u[.] v[.] w[.] x[.] y[.] z[.]),As(a[.] b[.] c[8] d[.] e[.] f[.] g[.] h[.] i[.] j[.] k[.] l[.] m[.] n[.] o[.] p[.] q[.] r[.] s[.] t[.] u[.] v[.] w[.] x[.] y[.] z[.]),Av(a[.] b[.] c[9] d[.] e[.] f[.] g[.] h[.] i[.] j[.] k[.] l[.] m[.] n[.] o[.] p[.] q[.] r[.] s[.] t[.] u[.] v[.] w[.] x[.] y[.] z[.])').
                             get_all_agents(),
                             [KappaAgent('Ac(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[2]{#} f[3]{#} g[.]{#} h[1]{#} i[4]{#} j[.]{#} k[.]{#} l[.]{#} m[5]{#} n[.]{#} o[.]{#} p[6]{#} q[7]{#} r[.]{#} s[8]{#} t[.]{#} u[.]{#} v[9]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})'),
                              KappaAgent('Ae(a[.]{#} b[.]{#} c[2]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})'),
                              KappaAgent('Af(a[.]{#} b[.]{#} c[3]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})'),
                              KappaAgent('Ah(a[.]{#} b[.]{#} c[1]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})'),
                              KappaAgent('Ai(a[.]{#} b[.]{#} c[4]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})'),
                              KappaAgent('Am(a[.]{#} b[.]{#} c[5]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})'),
                              KappaAgent('Ap(a[.]{#} b[.]{#} c[6]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})'),
                              KappaAgent('Aq(a[.]{#} b[.]{#} c[7]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})'),
                              KappaAgent('As(a[.]{#} b[.]{#} c[8]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})'),
                              KappaAgent('Av(a[.]{#} b[.]{#} c[9]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})')]
                         )
    def test_get_complex_composition(self):
        self.assertEqual(KappaComplex(
            'Ah(a[.] b[.] c[1] d[.] e[.] f[.] g[.] h[.] i[.] j[.] k[.] l[.] m[.] n[.] o[.] p[.] q[.] r[.] s[.] t[.] u[.] v[.] w[.] x[.] y[.] z[.]),Ac(a[.] b[.] c[.] d[.] e[2] f[3] g[.] h[1] i[4] j[.] k[.] l[.] m[5] n[.] o[.] p[6] q[7] r[.] s[8] t[.] u[.] v[9] w[.] x[.] y[.] z[.]),Ae(a[.] b[.] c[2] d[.] e[.] f[.] g[.] h[.] i[.] j[.] k[.] l[.] m[.] n[.] o[.] p[.] q[.] r[.] s[.] t[.] u[.] v[.] w[.] x[.] y[.] z[.]),Af(a[.] b[.] c[3] d[.] e[.] f[.] g[.] h[.] i[.] j[.] k[.] l[.] m[.] n[.] o[.] p[.] q[.] r[.] s[.] t[.] u[.] v[.] w[.] x[.] y[.] z[.]),Ai(a[.] b[.] c[4] d[.] e[.] f[.] g[.] h[.] i[.] j[.] k[.] l[.] m[.] n[.] o[.] p[.] q[.] r[.] s[.] t[.] u[.] v[.] w[.] x[.] y[.] z[.]),Am(a[.] b[.] c[5] d[.] e[.] f[.] g[.] h[.] i[.] j[.] k[.] l[.] m[.] n[.] o[.] p[.] q[.] r[.] s[.] t[.] u[.] v[.] w[.] x[.] y[.] z[.]),Ap(a[.] b[.] c[6] d[.] e[.] f[.] g[.] h[.] i[.] j[.] k[.] l[.] m[.] n[.] o[.] p[.] q[.] r[.] s[.] t[.] u[.] v[.] w[.] x[.] y[.] z[.]),Aq(a[.] b[.] c[7] d[.] e[.] f[.] g[.] h[.] i[.] j[.] k[.] l[.] m[.] n[.] o[.] p[.] q[.] r[.] s[.] t[.] u[.] v[.] w[.] x[.] y[.] z[.]),As(a[.] b[.] c[8] d[.] e[.] f[.] g[.] h[.] i[.] j[.] k[.] l[.] m[.] n[.] o[.] p[.] q[.] r[.] s[.] t[.] u[.] v[.] w[.] x[.] y[.] z[.]),Av(a[.] b[.] c[9] d[.] e[.] f[.] g[.] h[.] i[.] j[.] k[.] l[.] m[.] n[.] o[.] p[.] q[.] r[.] s[.] t[.] u[.] v[.] w[.] x[.] y[.] z[.])').
                             get_complex_composition(),
                             {KappaAgent('Ae()'): 1, KappaAgent('Ah()'): 1, KappaAgent('Ap()'): 1,
                              KappaAgent('Ai()'): 1, KappaAgent('Ac()'): 1, KappaAgent('Af()'): 1,
                              KappaAgent('As()'): 1, KappaAgent('Aq()'): 1, KappaAgent('Am()'): 1,
                              KappaAgent('Av()'): 1})

    def test_get_number_of_embeddings_of_agent(self):
        self.assertEqual(KappaComplex('Bob(bob[.]), bob(bob{ph}), jane(bob{un}[_])').
                         get_number_of_embeddings_of_agent('Bob'),1)
        self.assertEqual(KappaComplex('Bob(bob[.]), bob(bob{ph}), jane(bob{un}[_])').
                         get_number_of_embeddings_of_agent('bob'), 1)
        self.assertEqual(KappaComplex('Bob(bob[.]), bob(bob{ph}), jane(bob{un}[_])').
                         get_number_of_embeddings_of_agent('bob(bob[#])'), 1)
        self.assertEqual(KappaComplex('Bob(bob[.]), bob(bob{ph}), jane(bob{un}[_])').
                         get_number_of_embeddings_of_agent('jane(bob{#})'), 1)


#    def test_snapshot(self):

#    def test_rule(self):


if __name__ == '__main__':
    unittest.main()

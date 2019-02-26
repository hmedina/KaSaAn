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
        self.assertEqual(KappaComplex('_a(s1[1]{#}), _a(~b[3]{#}), _a(bob[2]{#} ~a[1]{#})').get_agent_types(),
                         {KappaAgent('_a')})

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


class TestKappaSnapshot(unittest.TestCase):
    """Testing various elements of KappaSnapshot representation."""
    snap_abc = KappaSnapshot('../models/alphabet_soup_snap.ka')
    snap_dim = KappaSnapshot('../models/dimerization_with_tokens_snap.ka')

    def test_snapshot_string_representation(self, ref_snap_abc = snap_abc, ref_snap_dim = snap_dim):
        self.assertEqual(str(ref_snap_abc)[0:1000],
                         '%init: 182 As(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})\n%init: 1 Ad(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[2]{#} i[.]{#} j[.]{#} k[3]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[1]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[4]{#}), Ah(a[.]{#} b[.]{#} c[.]{#} d[2]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Ak(a[.]{#} b[.]{#} c[.]{#} d[3]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Ap(a[.]{#} b[.]{#} c[.]{#} d[1]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#')
        self.assertEqual(str(ref_snap_dim),
                         '%init: 241.0 X\n%init: 241 A(a[1]{#}), A(a[1]{#})\n%init: 18 A(a[.]{#})')

    def test_get_snapshot_file_name(self, ref_snap_abc = snap_abc, ref_snap_dim = snap_dim):
        self.assertEqual(ref_snap_abc.get_snapshot_file_name(), 'alphabet_soup_snap.ka')
        self.assertEqual(ref_snap_dim.get_snapshot_file_name(), 'dimerization_with_tokens_snap.ka')

    def test_get_snapshot_time(self, ref_snap_abc = snap_abc, ref_snap_dim = snap_dim):
        self.assertEqual(ref_snap_abc.get_snapshot_time(), 10.0)
        self.assertEqual(ref_snap_dim.get_snapshot_time(), 10.0)

    def test_get_snapshot_uuid(self, ref_snap_abc = snap_abc, ref_snap_dim = snap_dim):
        self.assertEqual(ref_snap_abc.get_snapshot_uuid(), '466122889')
        self.assertEqual(ref_snap_dim.get_snapshot_uuid(), '912920752')

    def test_get_snapshot_event(self, ref_snap_abc = snap_abc, ref_snap_dim = snap_dim):
        self.assertEqual(ref_snap_abc.get_snapshot_event(), 91304)
        self.assertEqual(ref_snap_dim.get_snapshot_event(), 9953)

    def test_get_all_complexes(self, ref_snap_abc = snap_abc, ref_snap_dim = snap_dim):
        self.assertEqual(ref_snap_abc.get_all_complexes()[0:10],
                         [KappaComplex(
                             "As(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
                          KappaComplex(
                              "Ad(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[2]{#} i[.]{#} j[.]{#} k[3]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[1]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[4]{#}), Ah(a[.]{#} b[.]{#} c[.]{#} d[2]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Ak(a[.]{#} b[.]{#} c[.]{#} d[3]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Ap(a[.]{#} b[.]{#} c[.]{#} d[1]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Az(a[.]{#} b[.]{#} c[.]{#} d[4]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
                          KappaComplex(
                              "Ad(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[1]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[2]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[3]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[4]{#}), Ae(a[.]{#} b[.]{#} c[.]{#} d[1]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Aj(a[.]{#} b[.]{#} c[.]{#} d[2]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Ap(a[.]{#} b[.]{#} c[.]{#} d[3]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Az(a[.]{#} b[.]{#} c[.]{#} d[4]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
                          KappaComplex(
                              "Ay(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
                          KappaComplex(
                              "Av(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
                          KappaComplex(
                              "Ad(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[2]{#} p[.]{#} q[3]{#} r[1]{#} s[4]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[5]{#} y[.]{#} z[.]{#}), Ao(a[.]{#} b[.]{#} c[.]{#} d[2]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Aq(a[.]{#} b[.]{#} c[.]{#} d[3]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Ar(a[.]{#} b[.]{#} c[.]{#} d[1]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), As(a[.]{#} b[.]{#} c[.]{#} d[4]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Ax(a[.]{#} b[.]{#} c[.]{#} d[5]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
                          KappaComplex(
                              "Ac(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[2]{#} f[3]{#} g[.]{#} h[1]{#} i[4]{#} j[.]{#} k[.]{#} l[.]{#} m[5]{#} n[.]{#} o[.]{#} p[6]{#} q[7]{#} r[.]{#} s[8]{#} t[.]{#} u[.]{#} v[9]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Ae(a[.]{#} b[.]{#} c[2]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Af(a[.]{#} b[.]{#} c[3]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Ah(a[.]{#} b[.]{#} c[1]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Ai(a[.]{#} b[.]{#} c[4]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Am(a[.]{#} b[.]{#} c[5]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Ap(a[.]{#} b[.]{#} c[6]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Aq(a[.]{#} b[.]{#} c[7]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), As(a[.]{#} b[.]{#} c[8]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Av(a[.]{#} b[.]{#} c[9]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
                          KappaComplex(
                              "At(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
                          KappaComplex(
                              "Ad(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[2]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[3]{#} r[.]{#} s[1]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Aj(a[.]{#} b[.]{#} c[.]{#} d[2]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Aq(a[.]{#} b[.]{#} c[.]{#} d[3]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), As(a[.]{#} b[.]{#} c[.]{#} d[1]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
                          KappaComplex(
                              "Ao(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})")])
        self.assertEqual(len(ref_snap_abc.get_all_complexes()), 37)
        self.assertEqual(ref_snap_dim.get_all_complexes(),
                         [KappaComplex("A(a[1]{#}), A(a[1]{#})"), KappaComplex("A(a[.]{#})")])

    def test_get_all_abundances(self, ref_snap_abc = snap_abc, ref_snap_dim = snap_dim):
        self.assertEqual(ref_snap_abc.get_all_abundances(),
                         [182, 1, 1, 192, 189, 1, 1, 183, 1, 189, 190, 191, 176, 180, 1, 174, 187, 184, 183, 184, 190,
                          1, 171, 170, 1, 186, 1, 1, 185, 1, 1, 1, 1, 175, 185, 1, 182])
        self.assertEqual(ref_snap_dim.get_all_abundances(), [241, 18])

    def test_get_all_sizes(self, ref_snap_abc = snap_abc, ref_snap_dim = snap_dim):
        self.assertEqual(ref_snap_abc.get_all_sizes(), [1, 5, 5, 1, 1, 6, 10, 1, 4, 1, 1, 1, 1, 1, 21899, 1, 1, 1, 1,
                                                        1, 1, 2, 1, 1, 3, 1, 4, 4, 1, 5, 9, 5, 4, 1, 1, 7, 1])
        self.assertEqual(ref_snap_dim.get_all_sizes(), [2, 1])

    def test_get_agent_types_present(self, ref_snap_abc = snap_abc, ref_snap_dim = snap_dim):
        self.assertEqual(ref_snap_abc.get_agent_types_present(),
                         {KappaAgent("Aa()"), KappaAgent("Ab()"), KappaAgent("Ac()"), KappaAgent("Ad()"),
                          KappaAgent("Ae()"), KappaAgent("Af()"), KappaAgent("Ag()"), KappaAgent("Ah()"),
                          KappaAgent("Ai()"), KappaAgent("Aj()"), KappaAgent("Ak()"), KappaAgent("Al()"),
                          KappaAgent("Am()"), KappaAgent("An()"), KappaAgent("Ao()"), KappaAgent("Ap()"),
                          KappaAgent("Aq()"), KappaAgent("Ar()"), KappaAgent("As()"), KappaAgent("At()"),
                          KappaAgent("Au()"), KappaAgent("Av()"), KappaAgent("Aw()"), KappaAgent("Ax()"),
                          KappaAgent("Ay()"), KappaAgent("Az()")})
        self.assertEqual(ref_snap_dim.get_agent_types_present(), {KappaAgent("A()")})

    def test_get_all_complexes_and_abundances(self, ref_snap_dim = snap_dim):
        self.assertEqual(dict(ref_snap_dim.get_all_complexes_and_abundances()),
                         {KappaComplex('A(a[1]), A(a[1])'): 241,
                          KappaComplex('A(a[.])'): 18})

    def test_get_total_mass(self, ref_snap_abc = snap_abc, ref_snap_dim = snap_dim):
        self.assertEqual(ref_snap_abc.get_total_mass(), 26000)
        self.assertEqual(ref_snap_dim.get_total_mass(), 500)

    def test_get_complexes_with_abundance(self, ref_snap_abc = snap_abc, ref_snap_dim = snap_dim):
        self.assertEqual(ref_snap_abc.get_complexes_with_abundance(10), [])
        self.assertEqual(ref_snap_abc.get_complexes_with_abundance(190),
                         [KappaComplex("Ax(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
                          KappaComplex("Ag(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})")])
        self.assertEqual(ref_snap_dim.get_complexes_with_abundance(1), [])
        self.assertEqual(ref_snap_dim.get_complexes_with_abundance(18), [KappaComplex("A(a[.]{#})")])

    def test_get_complexes_of_size(self, ref_snap_abc = snap_abc, ref_snap_dim = snap_dim):
        self.assertEqual(ref_snap_abc.get_complexes_of_size(4),
                         [KappaComplex("Ad(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[2]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[3]{#} r[.]{#} s[1]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Aj(a[.]{#} b[.]{#} c[.]{#} d[2]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Aq(a[.]{#} b[.]{#} c[.]{#} d[3]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), As(a[.]{#} b[.]{#} c[.]{#} d[1]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
                          KappaComplex("Ad(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[2]{#} k[.]{#} l[.]{#} m[.]{#} n[1]{#} o[.]{#} p[.]{#} q[3]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Aj(a[.]{#} b[.]{#} c[.]{#} d[2]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), An(a[.]{#} b[.]{#} c[.]{#} d[1]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Aq(a[.]{#} b[.]{#} c[.]{#} d[3]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
                          KappaComplex("Ad(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[2]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[1]{#} q[.]{#} r[.]{#} s[.]{#} t[3]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Ak(a[.]{#} b[.]{#} c[.]{#} d[2]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Ap(a[.]{#} b[.]{#} c[.]{#} d[1]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), At(a[.]{#} b[.]{#} c[.]{#} d[3]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
                          KappaComplex("Ad(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[1]{#} h[.]{#} i[2]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[3]{#} x[.]{#} y[.]{#} z[.]{#}), Ag(a[.]{#} b[.]{#} c[.]{#} d[1]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Ai(a[.]{#} b[.]{#} c[.]{#} d[2]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Aw(a[.]{#} b[.]{#} c[.]{#} d[3]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})")])
        self.assertEqual(ref_snap_abc.get_complexes_of_size(8), [])
        self.assertEqual(ref_snap_dim.get_complexes_of_size(2), [KappaComplex("A(a[1]{#}), A(a[1]{#})")])
        self.assertEqual(ref_snap_dim.get_complexes_of_size(3), [])

    def test_get_largest_complexes(self, ref_snap_abc = snap_abc, ref_snap_dim = snap_dim):
        self.assertEqual(ref_snap_abc.get_largest_complexes()[0].get_number_of_bonds(), 78483)
        self.assertEqual(ref_snap_abc.get_largest_complexes()[0].get_size_of_complex(), 21899)
        self.assertEqual(ref_snap_abc.get_largest_complexes()[0].get_complex_composition(),
                         {KappaAgent("Ac()"): 997, KappaAgent("Ad()"): 992, KappaAgent("Ap()"): 811,
                          KappaAgent("Av()"): 808, KappaAgent("An()"): 823, KappaAgent("Ab()"): 998,
                          KappaAgent("Ak()"): 811, KappaAgent("Aj()"): 812, KappaAgent("Aa()"): 999,
                          KappaAgent("Az()"): 811, KappaAgent("Ax()"): 808, KappaAgent("Ag()"): 809,
                          KappaAgent("At()"): 815, KappaAgent("Aq()"): 810, KappaAgent("Ae()"): 828,
                          KappaAgent("Af()"): 825, KappaAgent("Am()"): 817, KappaAgent("Ah()"): 812,
                          KappaAgent("Aw()"): 821, KappaAgent("Ai()"): 812, KappaAgent("Ao()"): 808,
                          KappaAgent("Ay()"): 807, KappaAgent("As()"): 814, KappaAgent("Au()"): 808,
                          KappaAgent("Al()"): 826, KappaAgent("Ar()"): 817})
        self.assertEqual(ref_snap_dim.get_largest_complexes(), [KappaComplex("A(a[1]{#}), A(a[1]{#})")])

    def test_get_smallest_complexes(self, ref_snap_abc = snap_abc, ref_snap_dim = snap_dim):
        self.assertEqual(ref_snap_abc.get_smallest_complexes(), [
            KappaComplex("As(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
            KappaComplex("Ay(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
            KappaComplex("Av(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
            KappaComplex("At(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
            KappaComplex("Ao(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
            KappaComplex("Ax(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
            KappaComplex("Au(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
            KappaComplex("An(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
            KappaComplex("Am(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
            KappaComplex("Al(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
            KappaComplex("Ak(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
            KappaComplex("Aj(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
            KappaComplex("Ai(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
            KappaComplex("Ah(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
            KappaComplex("Ag(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
            KappaComplex("Af(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
            KappaComplex("Ae(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
            KappaComplex("Az(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
            KappaComplex("Aq(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
            KappaComplex("Aw(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
            KappaComplex("Ap(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
            KappaComplex("Ar(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})")])
        self.assertEqual(ref_snap_dim.get_smallest_complexes(), [KappaComplex("A(a[.]{#})")])

    def test_get_most_abundant_complexes(self, ref_snap_abc = snap_abc, ref_snap_dim = snap_dim):
        self.assertEqual(ref_snap_abc.get_most_abundant_complexes(), [KappaComplex("Ay(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})")])
        self.assertEqual(ref_snap_dim.get_most_abundant_complexes(), [KappaComplex("A(a[1]{#}), A(a[1]{#})")])

    def test_get_least_abundant_complexes(self, ref_snap_abc = snap_abc, ref_snap_dim = snap_dim):
        self.assertEqual(len(ref_snap_abc.get_least_abundant_complexes()), 15)
        self.assertEqual(ref_snap_abc.get_least_abundant_complexes()[0:3],
                         [KappaComplex("Ad(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[2]{#} i[.]{#} j[.]{#} k[3]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[1]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[4]{#}), Ah(a[.]{#} b[.]{#} c[.]{#} d[2]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Ak(a[.]{#} b[.]{#} c[.]{#} d[3]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Ap(a[.]{#} b[.]{#} c[.]{#} d[1]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Az(a[.]{#} b[.]{#} c[.]{#} d[4]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
                          KappaComplex("Ad(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[1]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[2]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[3]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[4]{#}), Ae(a[.]{#} b[.]{#} c[.]{#} d[1]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Aj(a[.]{#} b[.]{#} c[.]{#} d[2]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Ap(a[.]{#} b[.]{#} c[.]{#} d[3]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Az(a[.]{#} b[.]{#} c[.]{#} d[4]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
                          KappaComplex("Ad(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[2]{#} p[.]{#} q[3]{#} r[1]{#} s[4]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[5]{#} y[.]{#} z[.]{#}), Ao(a[.]{#} b[.]{#} c[.]{#} d[2]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Aq(a[.]{#} b[.]{#} c[.]{#} d[3]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Ar(a[.]{#} b[.]{#} c[.]{#} d[1]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), As(a[.]{#} b[.]{#} c[.]{#} d[4]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Ax(a[.]{#} b[.]{#} c[.]{#} d[5]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})")])
        self.assertEqual(ref_snap_dim.get_least_abundant_complexes(), [KappaComplex("A(a[.]{#})")])

    def test_get_size_distribution(self, ref_snap_abc = snap_abc, ref_snap_dim = snap_dim):
        self.assertEqual(ref_snap_abc.get_size_distribution(),
                         {1: 4028, 5: 4, 6: 1, 10: 1, 4: 4, 21899: 1, 2: 1, 3: 1, 9: 1, 7: 1})
        self.assertEqual(ref_snap_dim.get_size_distribution(), {2: 241, 1: 18})

    def test_get_all_tokens(self, ref_snap_dim = snap_dim):
        self.assertEqual(ref_snap_dim.get_all_tokens_and_values(), {'X': 241.0})

    def test_get_value_of_token(self, ref_snap_dim = snap_dim):
        self.assertEqual(ref_snap_dim.get_value_of_token('X'), 241.0)
        self.assertEqual(ref_snap_dim.get_value_of_token(KappaToken('X')), 241.0)

    def test_get_token_names(self, ref_snap_dim = snap_dim):
        self.assertEqual(ref_snap_dim.get_token_names(), ['X'])


#    def test_rule(self):


if __name__ == '__main__':
    unittest.main()

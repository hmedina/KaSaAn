#!/usr/bin/env python3

import unittest
from KaSaAn.core import KappaComplex, KappaAgent


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
                              KappaAgent('Av(a[.]{#} b[.]{#} c[9]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})')])

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
                         get_number_of_embeddings_of_agent('Bob'), 1)
        self.assertEqual(KappaComplex('Bob(bob[.]), bob(bob{ph}), jane(bob{un}[_])').
                         get_number_of_embeddings_of_agent('bob'), 1)
        self.assertEqual(KappaComplex('Bob(bob[.]), bob(bob{ph}), jane(bob{un}[_])').
                         get_number_of_embeddings_of_agent('bob(bob[#])'), 1)
        self.assertEqual(KappaComplex('Bob(bob[.]), bob(bob{ph}), jane(bob{un}[_])').
                         get_number_of_embeddings_of_agent('jane(bob{#})'), 1)

    def test_get_agent_identifiers(self):
        self.assertTrue(33 in KappaComplex('x22:A(s[2]), x33:A(s[1])').get_agent_identifiers())
        self.assertTrue(22 in KappaComplex('x22:A(s[2]), x33:A(s[1])').get_agent_identifiers())
        self.assertCountEqual([22, 33], KappaComplex('x22:A(s[2]), x33:A(s[1])').get_agent_identifiers())
        self.assertFalse(5 in KappaComplex('x22:A(s[2]), x33:A(s[1])').get_agent_identifiers())
        self.assertEqual([], KappaComplex('A(s[2]), A(s[1])').get_agent_identifiers())

    def test_to_networkx(self):
        unlabeled_snap = KappaComplex('A(b[1]), B(a[1] c[2]), C(b[2])')
        unlabeled_snap_ref_nodes = [(0, {'kappa': KappaAgent("A(b[1]{#})")}),
                                    (1, {'kappa': KappaAgent("B(a[1]{#} c[2]{#})")}),
                                    (2, {'kappa': KappaAgent("C(b[2]{#})")})]
        self.assertEqual(list(unlabeled_snap.to_networkx().nodes().items()), unlabeled_snap_ref_nodes)
        self.assertEqual(list(unlabeled_snap.to_networkx().edges()), [(0, 1), (1, 2)])
        labeled_snap = KappaComplex('x0:A(b[1]), x8:B(a[1] c[2]), x36:C(b[2])')
        labeled_snap_ref_nodes = [(0, {'kappa': KappaAgent("x0:A(b[1]{#})")}),
                                  (36, {'kappa': KappaAgent("x36:C(b[2]{#})")}),
                                  (8, {'kappa': KappaAgent("x8:B(a[1]{#} c[2]{#})")})]
        self.assertEqual(list(labeled_snap.to_networkx().nodes().items()), labeled_snap_ref_nodes)
        self.assertEqual(list(labeled_snap.to_networkx().edges()), [(0, 8), (36, 8)])

    def test_to_cytoscape_cx(self):
        ref_structure = [{'metaData': [{'name': 'nodes', 'version': '1.0'},
                                       {'name': 'nodeAttributes', 'version': '1.0'},
                                       {'name': 'edges', 'version': '1.0'},
                                       {'name': 'edgeAttributes', 'version': '1.0'},
                                       {'name': 'cyTablecolumn', 'version': '1.0'},
                                       {'name': 'networkAttributes', 'version': '1.0'}]}, {
                             'cyTableColumn': [{'applies_to': 'node_table', 'n': 'name'},
                                               {'applies_to': 'node_table', 'n': 'raw_expression'},
                                               {'applies_to': 'edge_table', 'n': 'name'},
                                               {'applies_to': 'edge_table', 'n': 's_agent_type'},
                                               {'applies_to': 'edge_table', 'n': 't_agent_type'},
                                               {'applies_to': 'edge_table', 'n': 's_port_name'},
                                               {'applies_to': 'edge_table', 'n': 't_port_name'},
                                               {'applies_to': 'edge_table', 'n': 'ident_in_snap'},
                                               {'applies_to': 'network_table', 'n': 'name'}]},
                         {'networkAttributes': [{'n': 'name', 'v': 'network'}]}, {
                             'nodes': [{'@id': 0, 'n': 'A'}, {'@id': 1, 'n': 'A'}, {'@id': 2, 'n': 'A'},
                                       {'@id': 3, 'n': 'A'}, {'@id': 4, 'n': 'B'}, {'@id': 5, 'n': 'B'},
                                       {'@id': 6, 'n': 'C'}]}, {
                             'edges': [{'s': 0, 't': 1, '@id': 7}, {'s': 0, 't': 3, '@id': 8},
                                       {'s': 1, 't': 2, '@id': 9}, {'s': 2, 't': 3, '@id': 10},
                                       {'s': 2, 't': 4, '@id': 11}, {'s': 4, 't': 5, '@id': 12},
                                       {'s': 5, 't': 6, '@id': 13}]}, {
                             'nodeAttributes': [{'po': 0, 'n': 'raw_expression', 'v': 'A(a[1]{ub} b[2]{#} c[.]{#})'},
                                                {'po': 1, 'n': 'raw_expression', 'v': 'A(a[2]{ph} b[3]{#} c[.]{#})'},
                                                {'po': 2, 'n': 'raw_expression', 'v': 'A(a[3]{ph} b[4]{#} c[5]{#})'},
                                                {'po': 3, 'n': 'raw_expression', 'v': 'A(a[4]{ph} b[1]{#} c[.]{#})'},
                                                {'po': 4, 'n': 'raw_expression', 'v': 'B(b[6]{#} c[5]{ub})'},
                                                {'po': 5, 'n': 'raw_expression', 'v': 'B(b[6]{#} c[7]{ph})'},
                                                {'po': 6, 'n': 'raw_expression', 'v': 'C(b[7]{#})'}]}, {
                             'edgeAttributes': [{'po': 7, 'n': 's_agent_type', 'v': 'A'},
                                                {'po': 7, 'n': 't_agent_type', 'v': 'A'},
                                                {'po': 7, 'n': 's_port_name', 'v': 'b'},
                                                {'po': 7, 'n': 't_port_name', 'v': 'a'},
                                                {'po': 7, 'n': 'ident_in_snap', 'v': '2'},
                                                {'po': 8, 'n': 's_agent_type', 'v': 'A'},
                                                {'po': 8, 'n': 't_agent_type', 'v': 'A'},
                                                {'po': 8, 'n': 's_port_name', 'v': 'a'},
                                                {'po': 8, 'n': 't_port_name', 'v': 'b'},
                                                {'po': 8, 'n': 'ident_in_snap', 'v': '1'},
                                                {'po': 9, 'n': 's_agent_type', 'v': 'A'},
                                                {'po': 9, 'n': 't_agent_type', 'v': 'A'},
                                                {'po': 9, 'n': 's_port_name', 'v': 'b'},
                                                {'po': 9, 'n': 't_port_name', 'v': 'a'},
                                                {'po': 9, 'n': 'ident_in_snap', 'v': '3'},
                                                {'po': 10, 'n': 's_agent_type', 'v': 'A'},
                                                {'po': 10, 'n': 't_agent_type', 'v': 'A'},
                                                {'po': 10, 'n': 's_port_name', 'v': 'b'},
                                                {'po': 10, 'n': 't_port_name', 'v': 'a'},
                                                {'po': 10, 'n': 'ident_in_snap', 'v': '4'},
                                                {'po': 11, 'n': 's_agent_type', 'v': 'A'},
                                                {'po': 11, 'n': 't_agent_type', 'v': 'B'},
                                                {'po': 11, 'n': 's_port_name', 'v': 'c'},
                                                {'po': 11, 'n': 't_port_name', 'v': 'c'},
                                                {'po': 11, 'n': 'ident_in_snap', 'v': '5'},
                                                {'po': 12, 'n': 's_agent_type', 'v': 'B'},
                                                {'po': 12, 'n': 't_agent_type', 'v': 'B'},
                                                {'po': 12, 'n': 's_port_name', 'v': 'b'},
                                                {'po': 12, 'n': 't_port_name', 'v': 'b'},
                                                {'po': 12, 'n': 'ident_in_snap', 'v': '6'},
                                                {'po': 13, 'n': 's_agent_type', 'v': 'B'},
                                                {'po': 13, 'n': 't_agent_type', 'v': 'C'},
                                                {'po': 13, 'n': 's_port_name', 'v': 'c'},
                                                {'po': 13, 'n': 't_port_name', 'v': 'b'},
                                                {'po': 13, 'n': 'ident_in_snap', 'v': '7'}]},
                         {'status': [{'error': '', 'success': True}]}]
        test_complex = KappaComplex("A(a[1]{ub} b[2]{#} c[.]{#}), A(a[2]{ph} b[3]{#} c[.]{#}), A(a[3]{ph} b[4]{#} c[5]{#}), A(a[4]{ph} b[1]{#} c[.]{#}), B(b[6]{#} c[5]{ub}), B(b[6]{#} c[7]{ph}), C(b[7]{#})")
        self.assertEqual(test_complex.to_cytoscape_cx(), ref_structure)

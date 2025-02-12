#!/usr/bin/env python3

import unittest
from KaSaAn.core import KappaAgent
from KaSaAn.core.KappaComplex import KappaComplex, NetMap, _edge_match, _node_match, _traverse_from


class TestKappaComplex(unittest.TestCase):
    """Testing various elements of KappaComplex representation."""
    def test_string_representation(self):
        self.assertEqual(str(KappaComplex('_a(s1[1]), ~b(~a[1], bob[2]), bob(~b[2])')),
                         '_a(s1[1]{#}), bob(~b[2]{#}), ~b(bob[2]{#} ~a[1]{#})')

    def test_get_number_of_bonds(self):
        self.assertEqual(KappaComplex('_a(s1[1]{#}), bob(~b[2]{#}), ~b(bob[2]{#} ~a[1]{#})').get_number_of_bonds(), 2)

    def test_get_agents_of_bond(self):
        self.assertCountEqual(
            KappaComplex('x0:A(a[0], b[1]), x1:A(a[1], b[2]), x2:A(a[2], b[0])').get_agents_of_bond(0),
            [KappaAgent('x0:A(a[0], b[1])'), KappaAgent('x2:A(a[2], b[0])')])
        self.assertCountEqual(
            KappaComplex('x0:A(a[0], b[1]), x1:A(a[1], b[2]), x2:A(a[2], b[0])').get_agents_of_bond(1),
            [KappaAgent('x0:A(a[0], b[1])'), KappaAgent('x1:A(a[1], b[2])')])
        self.assertCountEqual(
            KappaComplex('x0:A(a[0], b[1]), x1:A(a[1], b[2]), x2:A(a[2], b[0])').get_agents_of_bond(2),
            [KappaAgent('x2:A(a[2], b[0])'), KappaAgent('x1:A(a[1], b[2])')])
        self.assertIsNone(KappaComplex('x0:A(a[0], b[1]), x1:A(a[1], b[2]), x2:A(a[2], b[0])').get_agents_of_bond(3))

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

    def test_get_number_of_embeddings_of_complex(self):
        t1 = KappaComplex(
            'A(b[1]), B(a[1], b[2]{b}, c[4]), B(a[6], b[2]{a}, ba[3], bb[3], c[5]), C(b1[4]{s1}, b2[5]), A(b[6])')
        t2 = KappaComplex('A(b[1]), B(a[1])')
        t3 = KappaComplex('B(b[1]), B(b[1])')
        t4 = KappaComplex('B(b[1]{a}), B(b[1])')
        t5 = KappaComplex('B(b[1]{b}), B(b[1])')
        t6 = KappaComplex('Bob(h[3], t[1]), Bob(h[1], t[2]), Bob(h[2], t[3])')
        t7 = KappaComplex('A(h[4], t[1]), A(h[1], t[2]), A(h[2], t[3], b[5]), A(h[3], t[4], b[6]), B(a[5]), B(a[6], s{r})')
        self.assertEqual(0, t2.get_number_of_embeddings_of_complex(t3))
        self.assertEqual(2, t1.get_number_of_embeddings_of_complex(t2))
        self.assertEqual(1, t1.get_number_of_embeddings_of_complex(t3))
        self.assertEqual(2, t1.get_number_of_embeddings_of_complex(t3, False))
        self.assertEqual(1, t1.get_number_of_embeddings_of_complex(t4))
        self.assertEqual(1, t1.get_number_of_embeddings_of_complex(t5))
        self.assertEqual(1, t3.get_number_of_embeddings_of_complex(t3))
        self.assertEqual(2, t3.get_number_of_embeddings_of_complex(t3, False))
        self.assertEqual(1, t6.get_number_of_embeddings_of_complex(t6))
        self.assertEqual(3, t6.get_number_of_embeddings_of_complex(t6, False))
        self.assertEqual(1, t7.get_number_of_embeddings_of_complex(t7))
        self.assertEqual(1, t7.get_number_of_embeddings_of_complex(KappaComplex('A(h[4], t[1]), A(h[1], t[2]), A(h[2], t[3]), A(h[3], t[4])')))
        self.assertEqual(4, t7.get_number_of_embeddings_of_complex(KappaComplex('A(h[4], t[1]), A(h[1], t[2]), A(h[2], t[3]), A(h[3], t[4])'), False))
        self.assertEqual(2, t7.get_number_of_embeddings_of_complex(KappaComplex('A(h[41], t[11]), A(h[11], t[21]), A(h[21], t[31]), A(h[31], t[41], b[91]), B(a[91])')))
        self.assertEqual(2, t7.get_number_of_embeddings_of_complex(KappaComplex('A(h[41], t[11]), A(h[11], t[21]), A(h[21], t[31]), A(h[31], t[41], b[91]), B(a[91])'), False))
        self.assertEqual(1, t7.get_number_of_embeddings_of_complex(KappaComplex('A(h[41], t[11]), A(h[11], t[21]), A(h[21], t[31]), A(h[31], t[41], b[91]), B(a[91], s{r})')))
        self.assertEqual(0, t7.get_number_of_embeddings_of_complex(KappaComplex('A(h[41], t[11]), A(h[11], t[21]), A(h[21], t[31]), A(h[31], t[41], b[91]), B(a[91], s{x})')))
        self.assertEqual(2, t7.get_number_of_embeddings_of_complex(KappaComplex('A(b[9]), B(a[9])')))
        self.assertEqual(2, t7.get_number_of_embeddings_of_complex(KappaComplex('A(b[9]), B(a[9])'), False))

    def test_get_number_of_embeddings(self):
        t0 = KappaComplex(
            'A(b[1]), B(a[1], b[2]{b}, c[4]), B(a[6], b[2]{a}, ba[3], bb[3], c[5]), C(b1[4]{s1}, b2[5]), A(b[6])')
        c1 = KappaComplex('A(b[1]), B(a[1])')
        s1 = 'A(b[1]), B(a[1])'
        a2 = KappaAgent('B(b[_])')
        s2 = 'B(b[_])'
        sim = KappaComplex('Dvl(DEP[.]{#} DIX-head[1]{#} DIX-tail[2]{#} PDZ[.]{#} S407[.]{un} Y17[.]{un}), Dvl(DEP[.]{#} DIX-head[2]{#} DIX-tail[1]{#} PDZ[.]{#} S407[.]{un} Y17[.]{un})')
        self.assertEqual(t0.get_number_of_embeddings(c1), t0.get_number_of_embeddings(s1))
        self.assertEqual(t0.get_number_of_embeddings(a2), t0.get_number_of_embeddings(s2))
        self.assertEqual(sim.get_number_of_embeddings('Dvl(DIX-head[1]), Dvl(DIX-tail[1])'), 2)

    def test_get_agent_identifiers(self):
        self.assertTrue(33 in KappaComplex('x22:A(s[2]), x33:A(s[1])').get_agent_identifiers())
        self.assertTrue(22 in KappaComplex('x22:A(s[2]), x33:A(s[1])').get_agent_identifiers())
        self.assertCountEqual([22, 33], KappaComplex('x22:A(s[2]), x33:A(s[1])').get_agent_identifiers())
        self.assertFalse(5 in KappaComplex('x22:A(s[2]), x33:A(s[1])').get_agent_identifiers())
        self.assertCountEqual([], KappaComplex('A(s[2]), A(s[1])').get_agent_identifiers())

    def test_get_agent_from_identifier(self):
        self.assertEqual(KappaComplex('x1:A(s[2]), x2:B(s[2])').get_agent_from_identifier(1), KappaAgent('x1:A(s[2])'))
        self.assertEqual(KappaComplex('x3:A(s[3]), x2:B(s[3])').get_agent_from_identifier(2), KappaAgent('x2:B(s[3])'))
        self.assertIsNone(KappaComplex('x50:A(s[3]), x51:B(s[3])').get_agent_from_identifier(3))

    def test_to_networkx(self):
        unlabeled_snap = KappaComplex('A(b[1]), B(a[1] c[2]), C(b[2])')
        unlabeled_snap_ref_nodes = [(0, {'kappa': KappaAgent("A(b[1]{#})")}),
                                    (1, {'kappa': KappaAgent("B(a[1]{#} c[2]{#})")}),
                                    (2, {'kappa': KappaAgent("C(b[2]{#})")})]
        self.assertEqual(list(unlabeled_snap.to_networkx().nodes().items()), unlabeled_snap_ref_nodes)
        self.assertEqual(list(unlabeled_snap.to_networkx().edges()), [(0, 1), (1, 2)])
        labeled_snap = KappaComplex('x0:A(b[1]), x8:B(a[1] c[2]), x36:C(b[2])')
        labeled_snap_ref_nodes = [(0, {'kappa': KappaAgent("x0:A(b[1]{#})")}),
                                  (8, {'kappa': KappaAgent("x8:B(a[1]{#} c[2]{#})")}),
                                  (36, {'kappa': KappaAgent("x36:C(b[2]{#})")})
                                  ]
        self.assertEqual(list(labeled_snap.to_networkx().nodes().items()), labeled_snap_ref_nodes)
        self.assertEqual(list(labeled_snap.to_networkx().edges()), [(0, 8), (8, 36)])

    def test_to_cytoscape_cx(self):
        test_complex = KappaComplex("A(a[1]{ub} b[2]{#} c[.]{#}), A(a[2]{ph} b[3]{#} c[.]{#}), A(a[3]{ph} b[4]{#} c[5]{#}), A(a[4]{ph} b[1]{#} c[.]{#}), B(b[6]{#} c[5]{ub}), B(b[6]{#} c[7]{ph}), C(b[7]{#})")
        ref_metaData = [
            {'name': 'nodes', 'version': '1.0'},
            {'name': 'nodeAttributes', 'version': '1.0'},
            {'name': 'edges', 'version': '1.0'},
            {'name': 'edgeAttributes', 'version': '1.0'},
            {'name': 'cyTablecolumn', 'version': '1.0'},
            {'name': 'networkAttributes', 'version': '1.0'}]
        ref_cyTableColumn = [
            {'applies_to': 'node_table', 'n': 'name'},
            {'applies_to': 'node_table', 'n': 'raw_expression'},
            {'applies_to': 'edge_table', 'n': 'name'},
            {'applies_to': 'edge_table', 'n': 'bond_type'},
            {'applies_to': 'edge_table', 'n': 's_agent_type'},
            {'applies_to': 'edge_table', 'n': 't_agent_type'},
            {'applies_to': 'edge_table', 'n': 's_port_name'},
            {'applies_to': 'edge_table', 'n': 't_port_name'},
            {'applies_to': 'edge_table', 'n': 'ident_in_snap'},
            {'applies_to': 'network_table', 'n': 'name'}]
        ref_networkAttributes = [
            {'n': 'name', 'v': 'network'}]
        ref_nodes = [
            {'@id': 0, 'n': 'A'}, {'@id': 1, 'n': 'A'}, {'@id': 2, 'n': 'A'}, {'@id': 3, 'n': 'A'},
            {'@id': 4, 'n': 'B'}, {'@id': 5, 'n': 'B'}, {'@id': 6, 'n': 'C'}]
        ref_edges = [
            {'s': 0, 't': 1, '@id': 7}, {'s': 0, 't': 3, '@id': 8},
            {'s': 1, 't': 2, '@id': 9}, {'s': 2, 't': 3, '@id': 10},
            {'s': 2, 't': 4, '@id': 11}, {'s': 4, 't': 5, '@id': 12},
            {'s': 5, 't': 6, '@id': 13}]
        ref_nodeAttributes = [
            {'po': 0, 'n': 'raw_expression', 'v': 'A(a[1]{ub} b[2]{#} c[.]{#})'},
            {'po': 1, 'n': 'raw_expression', 'v': 'A(a[2]{ph} b[3]{#} c[.]{#})'},
            {'po': 2, 'n': 'raw_expression', 'v': 'A(a[3]{ph} b[4]{#} c[5]{#})'},
            {'po': 3, 'n': 'raw_expression', 'v': 'A(a[4]{ph} b[1]{#} c[.]{#})'},
            {'po': 4, 'n': 'raw_expression', 'v': 'B(b[6]{#} c[5]{ub})'},
            {'po': 5, 'n': 'raw_expression', 'v': 'B(b[6]{#} c[7]{ph})'},
            {'po': 6, 'n': 'raw_expression', 'v': 'C(b[7]{#})'}]
        ref_edgeAttributes = [
            {'po': 7, 'n': 'bond_type', 'v': 'A.b..a.A'},
            {'po': 7, 'n': 's_agent_type', 'v': 'A'},
            {'po': 7, 'n': 't_agent_type', 'v': 'A'},
            {'po': 7, 'n': 's_port_name', 'v': 'b'},
            {'po': 7, 'n': 't_port_name', 'v': 'a'},
            {'po': 7, 'n': 'ident_in_snap', 'v': '2'},
            {'po': 8, 'n': 'bond_type', 'v': 'A.a..b.A'},
            {'po': 8, 'n': 's_agent_type', 'v': 'A'},
            {'po': 8, 'n': 't_agent_type', 'v': 'A'},
            {'po': 8, 'n': 's_port_name', 'v': 'a'},
            {'po': 8, 'n': 't_port_name', 'v': 'b'},
            {'po': 8, 'n': 'ident_in_snap', 'v': '1'},
            {'po': 9, 'n': 'bond_type', 'v': 'A.b..a.A'},
            {'po': 9, 'n': 's_agent_type', 'v': 'A'},
            {'po': 9, 'n': 't_agent_type', 'v': 'A'},
            {'po': 9, 'n': 's_port_name', 'v': 'b'},
            {'po': 9, 'n': 't_port_name', 'v': 'a'},
            {'po': 9, 'n': 'ident_in_snap', 'v': '3'},
            {'po': 10, 'n': 'bond_type', 'v': 'A.b..a.A'},
            {'po': 10, 'n': 's_agent_type', 'v': 'A'},
            {'po': 10, 'n': 't_agent_type', 'v': 'A'},
            {'po': 10, 'n': 's_port_name', 'v': 'b'},
            {'po': 10, 'n': 't_port_name', 'v': 'a'},
            {'po': 10, 'n': 'ident_in_snap', 'v': '4'},
            {'po': 11, 'n': 'bond_type', 'v': 'A.c..c.B'},
            {'po': 11, 'n': 's_agent_type', 'v': 'A'},
            {'po': 11, 'n': 't_agent_type', 'v': 'B'},
            {'po': 11, 'n': 's_port_name', 'v': 'c'},
            {'po': 11, 'n': 't_port_name', 'v': 'c'},
            {'po': 11, 'n': 'ident_in_snap', 'v': '5'},
            {'po': 12, 'n': 'bond_type', 'v': 'B.b..b.B'},
            {'po': 12, 'n': 's_agent_type', 'v': 'B'},
            {'po': 12, 'n': 't_agent_type', 'v': 'B'},
            {'po': 12, 'n': 's_port_name', 'v': 'b'},
            {'po': 12, 'n': 't_port_name', 'v': 'b'},
            {'po': 12, 'n': 'ident_in_snap', 'v': '6'},
            {'po': 13, 'n': 'bond_type', 'v': 'B.c..b.C'},
            {'po': 13, 'n': 's_agent_type', 'v': 'B'},
            {'po': 13, 'n': 't_agent_type', 'v': 'C'},
            {'po': 13, 'n': 's_port_name', 'v': 'c'},
            {'po': 13, 'n': 't_port_name', 'v': 'b'},
            {'po': 13, 'n': 'ident_in_snap', 'v': '7'}]
        ref_status = [
            {'error': '', 'success': True}]
        comp_cx = test_complex.to_cytoscape_cx()
        self.assertEqual(comp_cx[0]['metaData'], ref_metaData)
        self.assertEqual(comp_cx[1]['cyTableColumn'], ref_cyTableColumn)
        self.assertEqual(comp_cx[2]['networkAttributes'], ref_networkAttributes)
        self.assertEqual(comp_cx[3]['nodes'], ref_nodes)
        self.assertEqual(comp_cx[4]['edges'], ref_edges)
        self.assertEqual(comp_cx[5]['nodeAttributes'], ref_nodeAttributes)
        self.assertEqual(comp_cx[6]['edgeAttributes'], ref_edgeAttributes)
        self.assertEqual(comp_cx[7]['status'], ref_status)

        ref_structure = [
            {'metaData': ref_metaData},
            {'cyTableColumn': ref_cyTableColumn},
            {'networkAttributes': ref_networkAttributes},
            {'nodes': ref_nodes},
            {'edges': ref_edges},
            {'nodeAttributes': ref_nodeAttributes},
            {'edgeAttributes': ref_edgeAttributes},
            {'status': ref_status}]
        self.assertEqual(comp_cx, ref_structure)

    def test_edge_match(self):
        kc_a = KappaComplex('x6:B(a[.] c[1]), x17:C(b[1])')
        kc_b = KappaComplex('x60:B(a[.] c[1]), x17:C(b[1])')
        kq = KappaComplex('B(a[.] c[1]), C(b[1])')
        self.assertTrue(_edge_match(kq.to_networkx(), kc_a.to_networkx(), 0, 6))
        self.assertTrue(_edge_match(kq.to_networkx(), kc_a.to_networkx(), 1, 17))
        self.assertTrue(_edge_match(kq.to_networkx(), kc_b.to_networkx(), 0, 60))
        self.assertTrue(_edge_match(kq.to_networkx(), kc_b.to_networkx(), 1, 17))
        self.assertFalse(_edge_match(kq.to_networkx(), kc_a.to_networkx(), 0, 17))
        self.assertFalse(_edge_match(kq.to_networkx(), kc_a.to_networkx(), 1, 6))
        self.assertFalse(_edge_match(kq.to_networkx(), kc_b.to_networkx(), 0, 17))
        self.assertFalse(_edge_match(kq.to_networkx(), kc_b.to_networkx(), 1, 60))

    def test_node_match(self):
        kc_a = KappaComplex('x6:B(a[.] c[1]), x17:C(b[1])')
        kc_b = KappaComplex('x60:B(a[.] c[1]), x17:C(b[1])')
        kq = KappaComplex('B(a[.] c[1]), C(b[1])')
        self.assertTrue(_node_match(kq.to_networkx(), kc_a.to_networkx(), 0, 6))
        self.assertTrue(_node_match(kq.to_networkx(), kc_a.to_networkx(), 1, 17))
        self.assertTrue(_node_match(kq.to_networkx(), kc_b.to_networkx(), 0, 60))
        self.assertTrue(_node_match(kq.to_networkx(), kc_b.to_networkx(), 1, 17))
        self.assertFalse(_node_match(kq.to_networkx(), kc_a.to_networkx(), 0, 17))
        self.assertFalse(_node_match(kq.to_networkx(), kc_a.to_networkx(), 1, 6))
        self.assertFalse(_node_match(kq.to_networkx(), kc_b.to_networkx(), 0, 17))
        self.assertFalse(_node_match(kq.to_networkx(), kc_b.to_networkx(), 1, 60))

    def test_traverse_from(self):
        kc_a = KappaComplex('x6:B(a[.] c[1]), x17:C(b[1])')
        kc_b = KappaComplex('x60:B(a[.] c[1]), x17:C(b[1])')
        kq = KappaComplex('B(a[.] c[1]), C(b[1])')
        nm_1 = NetMap()
        nm_1.edge_map.add((1, 1))
        nm_1.node_map.add((0, 6))
        nm_1.node_map.add((1, 17))
        self.assertEqual(nm_1, _traverse_from(kq.to_networkx(), kc_a.to_networkx(), 0, 6))
        nm_2 = NetMap()
        nm_2.edge_map.add((1, 1))
        nm_2.node_map.add((0, 60))
        nm_2.node_map.add((1, 17))
        self.assertEqual(nm_2, _traverse_from(kq.to_networkx(), kc_b.to_networkx(), 0, 60))
        ### testing against issue with simple rings and polymers
        # embed linear trimer into a linear tetramer
        polymer_4 = KappaComplex('x5:Axin(DIX-head[.] DIX-tail[3]), x6:Dvl(DIX-head[3] DIX-tail[2]), x7:Axin(DIX-head[2] DIX-tail[1]), x8:Dvl(DIX-head[1] DIX-tail[.])')
        pattern_lin = KappaComplex('Dvl(DIX-tail[0]), Axin(DIX-head[0], DIX-tail[1]), Dvl(DIX-head[1])')
        nm_3 = NetMap()
        nm_3.edge_map.add((1, 1))
        nm_3.edge_map.add((0, 2))
        nm_3.node_map.add((0, 7))
        nm_3.node_map.add((1, 8))
        nm_3.node_map.add((2, 6))
        self.assertEqual(nm_3, _traverse_from(pattern_lin.to_networkx(), polymer_4.to_networkx(), 0, 7))
        # do NOT embed cyclic heterodimer into linear pentamer
        pattern_cyc_a = KappaComplex('x0:Axin(DIX-head[1], DIX-tail[2]), x1:Dvl(DIX-head[2], DIX-tail[1])')
        polymer_5 = KappaComplex('x10:Axin(DIX-head[.], DIX-tail[1]), x11:Dvl(DIX-head[1], DIX-tail[2]), x12:Axin(DIX-head[2], DIX-tail[3]), x13:Dvl(DIX-head[3], DIX-tail[4]), x14:Axin(DIX-head[4], DIX-tail[.])')
        self.assertIsNone(_traverse_from(pattern_cyc_a.to_networkx(), polymer_4.to_networkx(), 0, 5))
        self.assertIsNone(_traverse_from(pattern_cyc_a.to_networkx(), polymer_4.to_networkx(), 0, 7))
        self.assertIsNone(_traverse_from(pattern_cyc_a.to_networkx(), polymer_4.to_networkx(), 1, 6))
        self.assertIsNone(_traverse_from(pattern_cyc_a.to_networkx(), polymer_4.to_networkx(), 1, 8))
        self.assertIsNone(_traverse_from(pattern_cyc_a.to_networkx(), polymer_5.to_networkx(), 0, 12))
        self.assertIsNone(_traverse_from(pattern_cyc_a.to_networkx(), polymer_5.to_networkx(), 1, 11))
        # as above, but with cyclic heterodimer written in "reverse", to guard against bond orientation mis-reading
        pattern_cyc_b = KappaComplex('x0:Dvl(DIX-head[1], DIX-tail[2]), x1:Axin(DIX-head[2], DIX-tail[1])')
        self.assertIsNone(_traverse_from(pattern_cyc_b.to_networkx(), polymer_5.to_networkx(), 0, 11))
        self.assertIsNone(_traverse_from(pattern_cyc_b.to_networkx(), polymer_5.to_networkx(), 0, 13))
        # the heterodimers should embed on each other when read correctly
        nm_cyclic_hetero_dimer = NetMap()
        nm_cyclic_hetero_dimer.edge_map.add((1, 2))
        nm_cyclic_hetero_dimer.edge_map.add((2, 1))
        nm_cyclic_hetero_dimer.node_map.add((0, 1))
        nm_cyclic_hetero_dimer.node_map.add((1, 0))
        self.assertEqual(nm_cyclic_hetero_dimer, _traverse_from(pattern_cyc_a.to_networkx(), pattern_cyc_b.to_networkx(), 0, 1))
        self.assertEqual(nm_cyclic_hetero_dimer, _traverse_from(pattern_cyc_a.to_networkx(), pattern_cyc_b.to_networkx(), 1, 0))
        self.assertEqual(nm_cyclic_hetero_dimer, _traverse_from(pattern_cyc_b.to_networkx(), pattern_cyc_a.to_networkx(), 0, 1))
        self.assertEqual(nm_cyclic_hetero_dimer, _traverse_from(pattern_cyc_b.to_networkx(), pattern_cyc_a.to_networkx(), 1, 0))
        # now with homopolymers, a cyclic homodimer against a linear homopentamer
        pattern_cyc_homo = KappaComplex('x0:Axin(DIX-head[1], DIX-tail[2]), x1:Axin(DIX-head[2], DIX-tail[1])')
        polymer_5_homo = KappaComplex('x10:Axin(DIX-head[.], DIX-tail[21]), x11:Axin(DIX-head[21], DIX-tail[22]), x12:Axin(DIX-head[22], DIX-tail[23]), x13:Axin(DIX-head[23], DIX-tail[24]), x14:Axin(DIX-head[24], DIX-tail[.])')
        self.assertIsNone(_traverse_from(pattern_cyc_homo.to_networkx(), polymer_5_homo.to_networkx(), 0, 10))
        self.assertIsNone(_traverse_from(pattern_cyc_homo.to_networkx(), polymer_5_homo.to_networkx(), 0, 11))
        self.assertIsNone(_traverse_from(pattern_cyc_homo.to_networkx(), polymer_5_homo.to_networkx(), 0, 12))
        self.assertIsNone(_traverse_from(pattern_cyc_homo.to_networkx(), polymer_5_homo.to_networkx(), 0, 13))
        self.assertIsNone(_traverse_from(pattern_cyc_homo.to_networkx(), polymer_5_homo.to_networkx(), 0, 14))
        self.assertIsNone(_traverse_from(pattern_cyc_homo.to_networkx(), polymer_5_homo.to_networkx(), 1, 10))
        self.assertIsNone(_traverse_from(pattern_cyc_homo.to_networkx(), polymer_5_homo.to_networkx(), 1, 11))
        self.assertIsNone(_traverse_from(pattern_cyc_homo.to_networkx(), polymer_5_homo.to_networkx(), 1, 12))
        self.assertIsNone(_traverse_from(pattern_cyc_homo.to_networkx(), polymer_5_homo.to_networkx(), 1, 13))
        self.assertIsNone(_traverse_from(pattern_cyc_homo.to_networkx(), polymer_5_homo.to_networkx(), 1, 14))
        pattern_3_homo = KappaComplex('x10:Axin(DIX-tail[21]), x11:Axin(DIX-head[21], DIX-tail[22]), x12:Axin(DIX-head[22])')
        self.assertIsNone(_traverse_from(pattern_3_homo.to_networkx(), pattern_cyc_homo.to_networkx(), 11, 0))
        self.assertIsNone(_traverse_from(pattern_3_homo.to_networkx(), pattern_cyc_homo.to_networkx(), 11, 1))
        # and for the positive case; automorphisms (also covered in test_get_number_of_embeddings_of_complex)
        nm_homo_cyclic_dimer_1 = NetMap()
        nm_homo_cyclic_dimer_1.edge_map.add((1, 1))
        nm_homo_cyclic_dimer_1.edge_map.add((2, 2))
        nm_homo_cyclic_dimer_1.node_map.add((0, 0))
        nm_homo_cyclic_dimer_1.node_map.add((1, 1))
        self.assertEqual(nm_homo_cyclic_dimer_1, _traverse_from(pattern_cyc_homo.to_networkx(), pattern_cyc_homo.to_networkx(), 0, 0))
        nm_homo_cyclic_dimer_2 = NetMap()
        nm_homo_cyclic_dimer_2.edge_map.add((1, 2))
        nm_homo_cyclic_dimer_2.edge_map.add((2, 1))
        nm_homo_cyclic_dimer_2.node_map.add((0, 1))
        nm_homo_cyclic_dimer_2.node_map.add((1, 0))
        self.assertEqual(nm_homo_cyclic_dimer_2, _traverse_from(pattern_cyc_homo.to_networkx(), pattern_cyc_homo.to_networkx(), 0, 1))

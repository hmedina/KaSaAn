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

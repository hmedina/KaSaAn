#!/usr/bin/env python3

import networkx
import unittest
from KaSaAn.core import KappaSnapshot, KappaComplex, KappaAgent, KappaToken


class TestKappaSnapshot(unittest.TestCase):
    """Testing various elements of KappaSnapshot representation."""
    snap_abc = KappaSnapshot('./models/alphabet_soup_snap.ka')
    snap_dim = KappaSnapshot('./models/dimerization_with_tokens_snap.ka')
    snap_kte = KappaSnapshot('./models/kite_snap.ka')
    snap_prz_labeled = KappaSnapshot('./models/labeled_vs_unlabeled_snapshots/prozone_snap_with_identifiers.ka')
    snap_prz_unlabeled = KappaSnapshot('./models/labeled_vs_unlabeled_snapshots/prozone_snap_no_identifiers.ka')
    snap_abc_raw = KappaSnapshot('./models/alphabet_soup_snap_raw.ka')

    def test_snapshot_string_representation(self, ref_snap_abc=snap_abc, ref_snap_dim=snap_dim):
        self.assertEqual(str(ref_snap_abc)[0:1000],
                         '%init: 182 As(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})\n%init: 1 Ad(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[2]{#} i[.]{#} j[.]{#} k[3]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[1]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[4]{#}), Ah(a[.]{#} b[.]{#} c[.]{#} d[2]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Ak(a[.]{#} b[.]{#} c[.]{#} d[3]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Ap(a[.]{#} b[.]{#} c[.]{#} d[1]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#')
        self.assertEqual(str(ref_snap_dim),
                         '%init: 241.0 X\n%init: 241 A(a[1]{#}), A(a[1]{#})\n%init: 18 A(a[.]{#})')

    def test_get_snapshot_file_name(self, ref_snap_abc=snap_abc, ref_snap_dim=snap_dim):
        self.assertEqual(ref_snap_abc.get_snapshot_file_name(), 'alphabet_soup_snap.ka')
        self.assertEqual(ref_snap_dim.get_snapshot_file_name(), 'dimerization_with_tokens_snap.ka')

    def test_get_snapshot_time(self, ref_snap_abc=snap_abc, ref_snap_dim=snap_dim, ref_snap_kte=snap_kte):
        self.assertEqual(ref_snap_abc.get_snapshot_time(), 10.0)
        self.assertEqual(ref_snap_dim.get_snapshot_time(), 10.0)
        self.assertEqual(ref_snap_kte.get_snapshot_time(), 1.0)

    def test_get_snapshot_uuid(self, ref_snap_abc=snap_abc, ref_snap_dim=snap_dim, ref_snap_kte=snap_kte):
        self.assertEqual(ref_snap_abc.get_snapshot_uuid(), '466122889')
        self.assertEqual(ref_snap_dim.get_snapshot_uuid(), '912920752')
        self.assertEqual(ref_snap_kte.get_snapshot_uuid(), '000000000')

    def test_get_snapshot_event(self, ref_snap_abc=snap_abc, ref_snap_dim=snap_dim, ref_snap_kte=snap_kte):
        self.assertEqual(ref_snap_abc.get_snapshot_event(), 91304)
        self.assertEqual(ref_snap_dim.get_snapshot_event(), 9953)
        self.assertEqual(ref_snap_kte.get_snapshot_event(), 1)

    def test_get_all_complexes(self, ref_snap_abc=snap_abc, ref_snap_dim=snap_dim):
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

    def test_get_all_abundances(self, ref_snap_abc=snap_abc, ref_snap_dim=snap_dim, ref_snap_kte=snap_kte):
        self.assertEqual(ref_snap_abc.get_all_abundances(),
                         [182, 1, 1, 192, 189, 1, 1, 183, 1, 189, 190, 191, 176, 180, 1, 174, 187, 184, 183, 184, 190,
                          1, 171, 170, 1, 186, 1, 1, 185, 1, 1, 1, 1, 175, 185, 1, 182])
        self.assertEqual(ref_snap_dim.get_all_abundances(), [241, 18])
        self.assertEqual(ref_snap_kte.get_all_abundances(), [1, 2])

    def test_get_all_sizes(self, ref_snap_abc=snap_abc, ref_snap_dim=snap_dim, ref_snap_kte=snap_kte):
        self.assertEqual(ref_snap_abc.get_all_sizes(), [1, 5, 5, 1, 1, 6, 10, 1, 4, 1, 1, 1, 1, 1, 21899, 1, 1, 1, 1,
                                                        1, 1, 2, 1, 1, 3, 1, 4, 4, 1, 5, 9, 5, 4, 1, 1, 7, 1])
        self.assertEqual(ref_snap_dim.get_all_sizes(), [2, 1])
        self.assertEqual(ref_snap_kte.get_all_sizes(), [7, 6])

    def test_get_agent_types_present(self, ref_snap_abc=snap_abc, ref_snap_dim=snap_dim, ref_snap_kte=snap_kte):
        self.assertEqual(ref_snap_abc.get_agent_types_present(),
                         {KappaAgent("Aa()"), KappaAgent("Ab()"), KappaAgent("Ac()"), KappaAgent("Ad()"),
                          KappaAgent("Ae()"), KappaAgent("Af()"), KappaAgent("Ag()"), KappaAgent("Ah()"),
                          KappaAgent("Ai()"), KappaAgent("Aj()"), KappaAgent("Ak()"), KappaAgent("Al()"),
                          KappaAgent("Am()"), KappaAgent("An()"), KappaAgent("Ao()"), KappaAgent("Ap()"),
                          KappaAgent("Aq()"), KappaAgent("Ar()"), KappaAgent("As()"), KappaAgent("At()"),
                          KappaAgent("Au()"), KappaAgent("Av()"), KappaAgent("Aw()"), KappaAgent("Ax()"),
                          KappaAgent("Ay()"), KappaAgent("Az()")})
        self.assertEqual(ref_snap_dim.get_agent_types_present(), {KappaAgent("A()")})
        self.assertEqual(ref_snap_kte.get_agent_types_present(),
                         {KappaAgent("A()"), KappaAgent("B()"), KappaAgent("C()")})

    def test_get_all_complexes_and_abundances(self, ref_snap_dim=snap_dim):
        self.assertEqual(dict(ref_snap_dim.get_all_complexes_and_abundances()),
                         {KappaComplex('A(a[1]), A(a[1])'): 241,
                          KappaComplex('A(a[.])'): 18})

    def test_get_total_mass(self, ref_snap_abc=snap_abc, ref_snap_dim=snap_dim, ref_snap_kte=snap_kte,
                            ref_snap_raw=snap_abc_raw):
        self.assertEqual(ref_snap_abc.get_total_mass(), 26000)
        self.assertEqual(ref_snap_dim.get_total_mass(), 500)
        self.assertEqual(ref_snap_kte.get_total_mass(), 19)
        self.assertEqual(ref_snap_raw.get_total_mass(), 26000)

    def test_get_abundance_of_agent(self, ref_snap_abc=snap_abc, ref_snap_dim=snap_dim, ref_snap_kte=snap_kte):
        self.assertEqual(ref_snap_abc.get_abundance_of_agent('Aa()'), 1000)
        self.assertEqual(ref_snap_abc.get_abundance_of_agent(KappaAgent('Aa()')), 1000)
        self.assertEqual(ref_snap_abc.get_abundance_of_agent('Aa(a[.])'), 30)
        self.assertEqual(ref_snap_abc.get_abundance_of_agent('Ab(b[.])'), 36)
        self.assertEqual(ref_snap_dim.get_abundance_of_agent('Bob()'), 0)
        self.assertEqual(ref_snap_dim.get_abundance_of_agent('A()'), 500)
        self.assertEqual(ref_snap_dim.get_abundance_of_agent('A(a[.])'), 18)
        self.assertEqual(ref_snap_dim.get_abundance_of_agent('A(a[_])'), 482)
        self.assertEqual(ref_snap_kte.get_abundance_of_agent('A(a{ph})'), 5)
        self.assertEqual(ref_snap_kte.get_abundance_of_agent('B(c{ph})'), 3)
        self.assertEqual(ref_snap_kte.get_abundance_of_agent('A(c[_])'), 3)

    def test_get_abundance_of_pattern(self, snap_wi_lab=snap_prz_labeled, snap_wo_lab=snap_prz_unlabeled, snap_kite=snap_kte):
        self.assertEqual((21, 21), snap_wi_lab.get_abundance_of_pattern('C(b[.])'))
        self.assertEqual((21, 21), snap_wo_lab.get_abundance_of_pattern('C(b[.])'))
        self.assertEqual((1, 1), snap_wi_lab.get_abundance_of_pattern('B(a[.] c[.])'))
        self.assertEqual((1, 1), snap_wo_lab.get_abundance_of_pattern('B(a[.] c[.])'))
        self.assertEqual((4, 4), snap_wi_lab.get_abundance_of_pattern('B(a[.] c[1]), C(b[1])'))
        self.assertEqual((4, 4), snap_wo_lab.get_abundance_of_pattern('B(a[.] c[1]), C(b[1])'))
        self.assertEqual((5, 5), snap_wi_lab.get_abundance_of_pattern('A(b[1]), B(a[1] c[2]), C(b[2])'))
        self.assertEqual((5, 5), snap_wo_lab.get_abundance_of_pattern('A(b[1]), B(a[1] c[2]), C(b[2])'))
        self.assertEqual((5, 5), snap_wi_lab.get_abundance_of_pattern('x23:A(b[1]), x54:B(a[1] c[2]), x97:C(b[2])'))
        self.assertEqual((5, 5), snap_wo_lab.get_abundance_of_pattern('x0:A(b[1]), x9:B(a[1] c[2]), x99:C(b[2])'))
        self.assertEqual((12, 3), snap_kite.get_abundance_of_pattern('A(a[4], b[1]), A(a[1], b[2]), A(a[2], b[3]), A(a[3], b[4])'))
        self.assertEqual(snap_kite.get_abundance_of_pattern('A(a[4], b[1]), A(a[1], b[2]), A(a[2], b[3]), A(a[3], b[4])', multi_thread=False), snap_kite.get_abundance_of_pattern('A(a[4], b[1]), A(a[1], b[2]), A(a[2], b[3]), A(a[3], b[4])', multi_thread=True))

    def test_get_composition(self, ref_snap_abc=snap_abc, ref_snap_dim=snap_dim, ref_snap_kte=snap_kte):
        self.assertEqual(ref_snap_abc.get_composition(),
                         {KappaAgent("Aa()"): 1000, KappaAgent("Ab()"): 1000, KappaAgent("Ac()"): 1000,
                          KappaAgent("Ad()"): 1000, KappaAgent("Ae()"): 1000, KappaAgent("Af()"): 1000,
                          KappaAgent("Ag()"): 1000, KappaAgent("Ah()"): 1000, KappaAgent("Ai()"): 1000,
                          KappaAgent("Aj()"): 1000, KappaAgent("Ak()"): 1000, KappaAgent("Al()"): 1000,
                          KappaAgent("Am()"): 1000, KappaAgent("An()"): 1000, KappaAgent("Ao()"): 1000,
                          KappaAgent("Ap()"): 1000, KappaAgent("Aq()"): 1000, KappaAgent("Ar()"): 1000,
                          KappaAgent("As()"): 1000, KappaAgent("At()"): 1000, KappaAgent("Au()"): 1000,
                          KappaAgent("Av()"): 1000, KappaAgent("Aw()"): 1000, KappaAgent("Ax()"): 1000,
                          KappaAgent("Ay()"): 1000, KappaAgent("Az()"): 1000})
        self.assertEqual(ref_snap_dim.get_composition(), {KappaAgent("A()"): 500})
        self.assertEqual(ref_snap_kte.get_composition(),
                         {KappaAgent('A()'): 12, KappaAgent('B()'): 6, KappaAgent('C()'): 1})

    def test_get_complexes_with_abundance(self, ref_snap_abc=snap_abc, ref_snap_dim=snap_dim):
        self.assertEqual(ref_snap_abc.get_complexes_with_abundance(10), [])
        self.assertEqual(ref_snap_abc.get_complexes_with_abundance(190),
                         [KappaComplex("Ax(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
                          KappaComplex("Ag(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})")])
        self.assertEqual(ref_snap_dim.get_complexes_with_abundance(1), [])
        self.assertEqual(ref_snap_dim.get_complexes_with_abundance(18), [KappaComplex("A(a[.]{#})")])

    def test_get_complexes_of_size(self, ref_snap_abc=snap_abc, ref_snap_dim=snap_dim):
        self.assertEqual(ref_snap_abc.get_complexes_of_size(4),
                         [(KappaComplex("Ad(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[2]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[3]{#} r[.]{#} s[1]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Aj(a[.]{#} b[.]{#} c[.]{#} d[2]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Aq(a[.]{#} b[.]{#} c[.]{#} d[3]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), As(a[.]{#} b[.]{#} c[.]{#} d[1]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"), 1),
                          (KappaComplex("Ad(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[2]{#} k[.]{#} l[.]{#} m[.]{#} n[1]{#} o[.]{#} p[.]{#} q[3]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Aj(a[.]{#} b[.]{#} c[.]{#} d[2]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), An(a[.]{#} b[.]{#} c[.]{#} d[1]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Aq(a[.]{#} b[.]{#} c[.]{#} d[3]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"), 1),
                          (KappaComplex("Ad(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[2]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[1]{#} q[.]{#} r[.]{#} s[.]{#} t[3]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Ak(a[.]{#} b[.]{#} c[.]{#} d[2]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Ap(a[.]{#} b[.]{#} c[.]{#} d[1]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), At(a[.]{#} b[.]{#} c[.]{#} d[3]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"), 1),
                          (KappaComplex("Ad(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[1]{#} h[.]{#} i[2]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[3]{#} x[.]{#} y[.]{#} z[.]{#}), Ag(a[.]{#} b[.]{#} c[.]{#} d[1]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Ai(a[.]{#} b[.]{#} c[.]{#} d[2]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Aw(a[.]{#} b[.]{#} c[.]{#} d[3]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"), 1)])
        self.assertEqual(ref_snap_abc.get_complexes_of_size(8), [])
        self.assertEqual(ref_snap_dim.get_complexes_of_size(2), [(KappaComplex("A(a[1]{#}), A(a[1]{#})"), 241)])
        self.assertEqual(ref_snap_dim.get_complexes_of_size(3), [])

    def test_get_largest_complexes(self, ref_snap_abc=snap_abc, ref_snap_dim=snap_dim):
        self.assertEqual(ref_snap_abc.get_largest_complexes()[0][0].get_number_of_bonds(), 78483)
        self.assertEqual(ref_snap_abc.get_largest_complexes()[0][0].get_size_of_complex(), 21899)
        self.assertEqual(ref_snap_abc.get_largest_complexes()[0][0].get_complex_composition(),
                         {KappaAgent("Ac()"): 997, KappaAgent("Ad()"): 992, KappaAgent("Ap()"): 811,
                          KappaAgent("Av()"): 808, KappaAgent("An()"): 823, KappaAgent("Ab()"): 998,
                          KappaAgent("Ak()"): 811, KappaAgent("Aj()"): 812, KappaAgent("Aa()"): 999,
                          KappaAgent("Az()"): 811, KappaAgent("Ax()"): 808, KappaAgent("Ag()"): 809,
                          KappaAgent("At()"): 815, KappaAgent("Aq()"): 810, KappaAgent("Ae()"): 828,
                          KappaAgent("Af()"): 825, KappaAgent("Am()"): 817, KappaAgent("Ah()"): 812,
                          KappaAgent("Aw()"): 821, KappaAgent("Ai()"): 812, KappaAgent("Ao()"): 808,
                          KappaAgent("Ay()"): 807, KappaAgent("As()"): 814, KappaAgent("Au()"): 808,
                          KappaAgent("Al()"): 826, KappaAgent("Ar()"): 817})
        self.assertEqual(ref_snap_dim.get_largest_complexes(), [(KappaComplex("A(a[1]{#}), A(a[1]{#})"), 241)])

    def test_get_smallest_complexes(self, ref_snap_abc=snap_abc, ref_snap_dim=snap_dim):
        self.assertEqual(ref_snap_abc.get_smallest_complexes(), [
            (KappaComplex("As(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"), 182),
            (KappaComplex("Ay(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"), 192),
            (KappaComplex("Av(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"), 189),
            (KappaComplex("At(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"), 183),
            (KappaComplex("Ao(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"), 189),
            (KappaComplex("Ax(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"), 190),
            (KappaComplex("Au(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"), 191),
            (KappaComplex("An(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"), 176),
            (KappaComplex("Am(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"), 180),
            (KappaComplex("Al(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"), 174),
            (KappaComplex("Ak(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"), 187),
            (KappaComplex("Aj(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"), 184),
            (KappaComplex("Ai(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"), 183),
            (KappaComplex("Ah(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"), 184),
            (KappaComplex("Ag(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"), 190),
            (KappaComplex("Af(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"), 171),
            (KappaComplex("Ae(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"), 170),
            (KappaComplex("Az(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"), 186),
            (KappaComplex("Aq(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"), 185),
            (KappaComplex("Aw(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"), 175),
            (KappaComplex("Ap(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"), 185),
            (KappaComplex("Ar(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"), 182)])
        self.assertEqual(ref_snap_dim.get_smallest_complexes(), [(KappaComplex("A(a[.]{#})"), 18)])

    def test_get_most_abundant_complexes(self, ref_snap_abc=snap_abc, ref_snap_dim=snap_dim):
        self.assertEqual(ref_snap_abc.get_most_abundant_complexes(), [KappaComplex("Ay(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})")])
        self.assertEqual(ref_snap_dim.get_most_abundant_complexes(), [KappaComplex("A(a[1]{#}), A(a[1]{#})")])

    def test_get_least_abundant_complexes(self, ref_snap_abc=snap_abc, ref_snap_dim=snap_dim):
        self.assertEqual(len(ref_snap_abc.get_least_abundant_complexes()), 15)
        self.assertEqual(ref_snap_abc.get_least_abundant_complexes()[0:3],
                         [KappaComplex("Ad(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[2]{#} i[.]{#} j[.]{#} k[3]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[1]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[4]{#}), Ah(a[.]{#} b[.]{#} c[.]{#} d[2]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Ak(a[.]{#} b[.]{#} c[.]{#} d[3]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Ap(a[.]{#} b[.]{#} c[.]{#} d[1]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Az(a[.]{#} b[.]{#} c[.]{#} d[4]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
                          KappaComplex("Ad(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[1]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[2]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[3]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[4]{#}), Ae(a[.]{#} b[.]{#} c[.]{#} d[1]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Aj(a[.]{#} b[.]{#} c[.]{#} d[2]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Ap(a[.]{#} b[.]{#} c[.]{#} d[3]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Az(a[.]{#} b[.]{#} c[.]{#} d[4]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})"),
                          KappaComplex("Ad(a[.]{#} b[.]{#} c[.]{#} d[.]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[2]{#} p[.]{#} q[3]{#} r[1]{#} s[4]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[5]{#} y[.]{#} z[.]{#}), Ao(a[.]{#} b[.]{#} c[.]{#} d[2]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Aq(a[.]{#} b[.]{#} c[.]{#} d[3]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Ar(a[.]{#} b[.]{#} c[.]{#} d[1]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), As(a[.]{#} b[.]{#} c[.]{#} d[4]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#}), Ax(a[.]{#} b[.]{#} c[.]{#} d[5]{#} e[.]{#} f[.]{#} g[.]{#} h[.]{#} i[.]{#} j[.]{#} k[.]{#} l[.]{#} m[.]{#} n[.]{#} o[.]{#} p[.]{#} q[.]{#} r[.]{#} s[.]{#} t[.]{#} u[.]{#} v[.]{#} w[.]{#} x[.]{#} y[.]{#} z[.]{#})")])
        self.assertEqual(ref_snap_dim.get_least_abundant_complexes(), [KappaComplex("A(a[.]{#})")])

    def test_get_size_distribution(self, ref_snap_abc=snap_abc, ref_snap_dim=snap_dim, ref_snap_kte=snap_kte):
        self.assertEqual(ref_snap_abc.get_size_distribution(),
                         {1: 4028, 2: 1, 3: 1, 4: 4, 5: 4, 6: 1, 7: 1, 9: 1, 10: 1, 21899: 1})
        self.assertEqual(ref_snap_dim.get_size_distribution(), {1: 18, 2: 241})
        self.assertEqual(ref_snap_kte.get_size_distribution(), {6: 2, 7: 1})

    def test_get_all_tokens(self, ref_snap_dim=snap_dim, ref_snap_kte=snap_kte):
        self.assertEqual(ref_snap_dim.get_all_tokens_and_values(), {'X': 241.0})
        self.assertEqual(ref_snap_kte.get_all_tokens_and_values(), {})

    def test_get_value_of_token(self, ref_snap_dim=snap_dim):
        self.assertEqual(ref_snap_dim.get_value_of_token('X'), 241.0)
        self.assertEqual(ref_snap_dim.get_value_of_token(KappaToken('X')), 241.0)

    def test_get_token_names(self, ref_snap_dim=snap_dim):
        self.assertEqual(ref_snap_dim.get_token_names(), ['X'])

    def test_get_agent_identifiers(self, ref_snap_raw=snap_abc_raw, ref_snap_triaged=snap_abc):
        self.assertEqual([], ref_snap_triaged.get_agent_identifiers())
        self.assertCountEqual(list(range(0, 26000)), ref_snap_raw.get_agent_identifiers())

    def test_find_complex_of_agent(self, ref_snap_raw=snap_abc_raw, ref_snap_triaged=snap_abc):
        self.assertEqual(ref_snap_raw.get_complex_of_agent(25918), KappaComplex('x25918:Aw(a[.] b[.] c[.] d[.] e[.] f[.] g[.] h[.] i[.] j[.] k[.] l[.] m[.] n[.] o[.] p[.] q[.] r[.] s[.] t[.] u[.] v[.] w[.] x[.] y[.] z[.])'))
        self.assertEqual(ref_snap_raw.get_complex_of_agent(0).get_size_of_complex(), 21918)
        self.assertIsNone(ref_snap_triaged.get_complex_of_agent(1))

    def test_get_agent_from_identifier(self, ref_snap_raw=snap_abc_raw, ref_snap_triaged=snap_abc):
        self.assertEqual(ref_snap_raw.get_agent_from_identifier(0), KappaAgent('x0:Aa(a[1] b[2] c[3] d[4] e[5] f[.] g[.] h[6] i[.] j[7] k[8] l[9] m[10] n[11] o[12] p[13] q[14] r[15] s[.] t[16] u[17] v[18] w[19] x[20] y[21] z[22])'))
        self.assertIsNone(ref_snap_triaged.get_agent_from_identifier(0))

    def test_to_networkx(self, ref_snap_abc=snap_abc, ref_snap_dim=snap_dim, ref_snap_kte=snap_kte,
                         ref_labeled=snap_prz_labeled, ref_unlabeled=snap_prz_unlabeled):
        self.assertEqual(ref_snap_abc.to_networkx().number_of_nodes(), 26000)
        self.assertEqual(ref_snap_abc.to_networkx().number_of_edges(), 78542)
        self.assertEqual(ref_snap_dim.to_networkx().number_of_nodes(), 500)
        self.assertEqual(ref_snap_dim.to_networkx().number_of_edges(), 241)
        self.assertEqual(ref_snap_kte.to_networkx().number_of_nodes(), 19)
        self.assertEqual(ref_snap_kte.to_networkx().number_of_edges(), 19)
        self.assertCountEqual(ref_labeled.to_networkx().nodes(), ref_unlabeled.to_networkx().nodes())
        self.assertEqual(len(ref_labeled.to_networkx().edges()), len(ref_unlabeled.to_networkx().edges))
        self.assertEqual(networkx.degree_histogram(ref_labeled.to_networkx()),
                         networkx.degree_histogram(ref_unlabeled.to_networkx()))
        self.assertEqual(list(networkx.selfloop_edges(ref_labeled.to_networkx())), [])
        self.assertEqual(list(networkx.selfloop_edges(ref_unlabeled.to_networkx())), [])

    def test_to_cytoscape_cx(self, ref_snap_kte=snap_kte):
        ref_metaData = [
            {"name": "nodes", "version": "1.0"},
            {"name": "nodeAttributes", "version": "1.0"},
            {"name": "edges", "version": "1.0"},
            {"name": "edgeAttributes", "version": "1.0"},
            {"name": "cyTablecolumn", "version": "1.0"},
            {"name": "networkAttributes", "version": "1.0"}]
        ref_cyTableColumn = [
            {"applies_to": "node_table", "n": "name"},
            {"applies_to": "node_table", "n": "raw_expression"},
            {"applies_to": "edge_table", "n": "name"},
            {'applies_to': 'edge_table', 'n': 'bond_type'},
            {"applies_to": "edge_table", "n": "s_agent_type"},
            {"applies_to": "edge_table", "n": "t_agent_type"},
            {"applies_to": "edge_table", "n": "s_port_name"},
            {"applies_to": "edge_table", "n": "t_port_name"},
            {"applies_to": "edge_table", "n": "ident_in_snap"},
            {"applies_to": "network_table", "n": "name"}]
        ref_networkAttributes = [
            {"n": "name", "v": "kite_snap.ka"},
            {"n": "time", "v": 1.0},
            {"n": "event", "v": 1},
            {"n": "UUID", "v": "000000000"}]
        ref_nodes = [
            {"@id": 0, "n": "A"}, {"@id": 1, "n": "A"}, {"@id": 2, "n": "A"}, {"@id": 3, "n": "A"},
            {"@id": 4, "n": "B"}, {"@id": 5, "n": "B"}, {"@id": 6, "n": "C"}, {"@id": 7, "n": "A"},
            {"@id": 8, "n": "A"}, {"@id": 9, "n": "A"}, {"@id": 10, "n": "A"}, {"@id": 11, "n": "B"},
            {"@id": 12, "n": "B"}, {"@id": 13, "n": "A"}, {"@id": 14, "n": "A"}, {"@id": 15, "n": "A"},
            {"@id": 16, "n": "A"}, {"@id": 17, "n": "B"}, {"@id": 18, "n": "B"}]
        ref_edges = [
            {"s": 0, "t": 1, "@id": 19}, {"s": 0, "t": 3, "@id": 20}, {"s": 1, "t": 2, "@id": 21},
            {"s": 2, "t": 3, "@id": 22}, {"s": 2, "t": 4, "@id": 23}, {"s": 4, "t": 5, "@id": 24},
            {"s": 5, "t": 6, "@id": 25}, {"s": 7, "t": 8, "@id": 26}, {"s": 7, "t": 10, "@id": 27},
            {"s": 8, "t": 9, "@id": 28}, {"s": 9, "t": 10, "@id": 29}, {"s": 9, "t": 12, "@id": 30},
            {"s": 11, "t": 12, "@id": 31}, {"s": 13, "t": 14, "@id": 32}, {"s": 13, "t": 16, "@id": 33},
            {"s": 14, "t": 15, "@id": 34}, {"s": 15, "t": 16, "@id": 35}, {"s": 15, "t": 18, "@id": 36},
            {"s": 17, "t": 18, "@id": 37}]
        ref_nodeAttributes = [
            {"po": 0, "n": "raw_expression", "v": "A(a[1]{ub} b[2]{#} c[.]{#})"},
            {"po": 1, "n": "raw_expression", "v": "A(a[2]{ph} b[3]{#} c[.]{#})"},
            {"po": 2, "n": "raw_expression", "v": "A(a[3]{ph} b[4]{#} c[5]{#})"},
            {"po": 3, "n": "raw_expression", "v": "A(a[4]{ph} b[1]{#} c[.]{#})"},
            {"po": 4, "n": "raw_expression", "v": "B(b[6]{#} c[5]{ub})"},
            {"po": 5, "n": "raw_expression", "v": "B(b[6]{#} c[7]{ph})"},
            {"po": 6, "n": "raw_expression", "v": "C(b[7]{#})"},
            {"po": 7, "n": "raw_expression", "v": "A(a[1]{ph} b[2]{#} c[.]{#})"},
            {"po": 8, "n": "raw_expression", "v": "A(a[2]{ub} b[3]{#} c[.]{#})"},
            {"po": 9, "n": "raw_expression", "v": "A(a[3]{ub} b[4]{#} c[5]{#})"},
            {"po": 10, "n": "raw_expression", "v": "A(a[4]{ub} b[1]{#} c[.]{#})"},
            {"po": 11, "n": "raw_expression", "v": "B(b[6]{#} c[.]{ub})"},
            {"po": 12, "n": "raw_expression", "v": "B(b[6]{#} c[5]{ph})"},
            {"po": 13, "n": "raw_expression", "v": "A(a[1]{ph} b[2]{#} c[.]{#})"},
            {"po": 14, "n": "raw_expression", "v": "A(a[2]{ub} b[3]{#} c[.]{#})"},
            {"po": 15, "n": "raw_expression", "v": "A(a[3]{ub} b[4]{#} c[5]{#})"},
            {"po": 16, "n": "raw_expression", "v": "A(a[4]{ub} b[1]{#} c[.]{#})"},
            {"po": 17, "n": "raw_expression", "v": "B(b[6]{#} c[.]{ub})"},
            {"po": 18, "n": "raw_expression", "v": "B(b[6]{#} c[5]{ph})"}]
        ref_edgeAttributes = [
            {"po": 19, "n": "bond_type", "v": "A.b..a.A"},
            {"po": 19, "n": "s_agent_type", "v": "A"},
            {"po": 19, "n": "t_agent_type", "v": "A"},
            {"po": 19, "n": "s_port_name", "v": "b"},
            {"po": 19, "n": "t_port_name", "v": "a"},
            {"po": 19, "n": "ident_in_snap", "v": "2"},
            {"po": 20, "n": "bond_type", "v": "A.a..b.A"},
            {"po": 20, "n": "s_agent_type", "v": "A"},
            {"po": 20, "n": "t_agent_type", "v": "A"},
            {"po": 20, "n": "s_port_name", "v": "a"},
            {"po": 20, "n": "t_port_name", "v": "b"},
            {"po": 20, "n": "ident_in_snap", "v": "1"},
            {"po": 21, "n": "bond_type", "v": "A.b..a.A"},
            {"po": 21, "n": "s_agent_type", "v": "A"},
            {"po": 21, "n": "t_agent_type", "v": "A"},
            {"po": 21, "n": "s_port_name", "v": "b"},
            {"po": 21, "n": "t_port_name", "v": "a"},
            {"po": 21, "n": "ident_in_snap", "v": "3"},
            {"po": 22, "n": "bond_type", "v": "A.b..a.A"},
            {"po": 22, "n": "s_agent_type", "v": "A"},
            {"po": 22, "n": "t_agent_type", "v": "A"},
            {"po": 22, "n": "s_port_name", "v": "b"},
            {"po": 22, "n": "t_port_name", "v": "a"},
            {"po": 22, "n": "ident_in_snap", "v": "4"},
            {"po": 23, "n": "bond_type", "v": "A.c..c.B"},
            {"po": 23, "n": "s_agent_type", "v": "A"},
            {"po": 23, "n": "t_agent_type", "v": "B"},
            {"po": 23, "n": "s_port_name", "v": "c"},
            {"po": 23, "n": "t_port_name", "v": "c"},
            {"po": 23, "n": "ident_in_snap", "v": "5"},
            {"po": 24, "n": "bond_type", "v": "B.b..b.B"},
            {"po": 24, "n": "s_agent_type", "v": "B"},
            {"po": 24, "n": "t_agent_type", "v": "B"},
            {"po": 24, "n": "s_port_name", "v": "b"},
            {"po": 24, "n": "t_port_name", "v": "b"},
            {"po": 24, "n": "ident_in_snap", "v": "6"},
            {"po": 25, "n": "bond_type", "v": "B.c..b.C"},
            {"po": 25, "n": "s_agent_type", "v": "B"},
            {"po": 25, "n": "t_agent_type", "v": "C"},
            {"po": 25, "n": "s_port_name", "v": "c"},
            {"po": 25, "n": "t_port_name", "v": "b"},
            {"po": 25, "n": "ident_in_snap", "v": "7"},
            {"po": 26, "n": "bond_type", "v": "A.b..a.A"},
            {"po": 26, "n": "s_agent_type", "v": "A"},
            {"po": 26, "n": "t_agent_type", "v": "A"},
            {"po": 26, "n": "s_port_name", "v": "b"},
            {"po": 26, "n": "t_port_name", "v": "a"},
            {"po": 26, "n": "ident_in_snap", "v": "2"},
            {"po": 27, "n": "bond_type", "v": "A.a..b.A"},
            {"po": 27, "n": "s_agent_type", "v": "A"},
            {"po": 27, "n": "t_agent_type", "v": "A"},
            {"po": 27, "n": "s_port_name", "v": "a"},
            {"po": 27, "n": "t_port_name", "v": "b"},
            {"po": 27, "n": "ident_in_snap", "v": "1"},
            {"po": 28, "n": "bond_type", "v": "A.b..a.A"},
            {"po": 28, "n": "s_agent_type", "v": "A"},
            {"po": 28, "n": "t_agent_type", "v": "A"},
            {"po": 28, "n": "s_port_name", "v": "b"},
            {"po": 28, "n": "t_port_name", "v": "a"},
            {"po": 28, "n": "ident_in_snap", "v": "3"},
            {"po": 29, "n": "bond_type", "v": "A.b..a.A"},
            {"po": 29, "n": "s_agent_type", "v": "A"},
            {"po": 29, "n": "t_agent_type", "v": "A"},
            {"po": 29, "n": "s_port_name", "v": "b"},
            {"po": 29, "n": "t_port_name", "v": "a"},
            {"po": 29, "n": "ident_in_snap", "v": "4"},
            {"po": 30, "n": "bond_type", "v": "A.c..c.B"},
            {"po": 30, "n": "s_agent_type", "v": "A"},
            {"po": 30, "n": "t_agent_type", "v": "B"},
            {"po": 30, "n": "s_port_name", "v": "c"},
            {"po": 30, "n": "t_port_name", "v": "c"},
            {"po": 30, "n": "ident_in_snap", "v": "5"},
            {"po": 31, "n": "bond_type", "v": "B.b..b.B"},
            {"po": 31, "n": "s_agent_type", "v": "B"},
            {"po": 31, "n": "t_agent_type", "v": "B"},
            {"po": 31, "n": "s_port_name", "v": "b"},
            {"po": 31, "n": "t_port_name", "v": "b"},
            {"po": 31, "n": "ident_in_snap", "v": "6"},
            {"po": 32, "n": "bond_type", "v": "A.b..a.A"},
            {"po": 32, "n": "s_agent_type", "v": "A"},
            {"po": 32, "n": "t_agent_type", "v": "A"},
            {"po": 32, "n": "s_port_name", "v": "b"},
            {"po": 32, "n": "t_port_name", "v": "a"},
            {"po": 32, "n": "ident_in_snap", "v": "2"},
            {"po": 33, "n": "bond_type", "v": "A.a..b.A"},
            {"po": 33, "n": "s_agent_type", "v": "A"},
            {"po": 33, "n": "t_agent_type", "v": "A"},
            {"po": 33, "n": "s_port_name", "v": "a"},
            {"po": 33, "n": "t_port_name", "v": "b"},
            {"po": 33, "n": "ident_in_snap", "v": "1"},
            {"po": 34, "n": "bond_type", "v": "A.b..a.A"},
            {"po": 34, "n": "s_agent_type", "v": "A"},
            {"po": 34, "n": "t_agent_type", "v": "A"},
            {"po": 34, "n": "s_port_name", "v": "b"},
            {"po": 34, "n": "t_port_name", "v": "a"},
            {"po": 34, "n": "ident_in_snap", "v": "3"},
            {"po": 35, "n": "bond_type", "v": "A.b..a.A"},
            {"po": 35, "n": "s_agent_type", "v": "A"},
            {"po": 35, "n": "t_agent_type", "v": "A"},
            {"po": 35, "n": "s_port_name", "v": "b"},
            {"po": 35, "n": "t_port_name", "v": "a"},
            {"po": 35, "n": "ident_in_snap", "v": "4"},
            {"po": 36, "n": "bond_type", "v": "A.c..c.B"},
            {"po": 36, "n": "s_agent_type", "v": "A"},
            {"po": 36, "n": "t_agent_type", "v": "B"},
            {"po": 36, "n": "s_port_name", "v": "c"},
            {"po": 36, "n": "t_port_name", "v": "c"},
            {"po": 36, "n": "ident_in_snap", "v": "5"},
            {"po": 37, "n": "bond_type", "v": "B.b..b.B"},
            {"po": 37, "n": "s_agent_type", "v": "B"},
            {"po": 37, "n": "t_agent_type", "v": "B"},
            {"po": 37, "n": "s_port_name", "v": "b"},
            {"po": 37, "n": "t_port_name", "v": "b"},
            {"po": 37, "n": "ident_in_snap", "v": "6"}]
        ref_status = [{"error": "", "success": True}]
        snap_cx = ref_snap_kte.to_cytoscape_cx()
        self.assertEqual(snap_cx[0]['metaData'], ref_metaData)
        self.assertEqual(snap_cx[1]['cyTableColumn'], ref_cyTableColumn)
        self.assertEqual(snap_cx[2]['networkAttributes'], ref_networkAttributes)
        self.assertEqual(snap_cx[3]['nodes'], ref_nodes)
        self.assertEqual(snap_cx[4]['edges'], ref_edges)
        self.assertEqual(snap_cx[5]['nodeAttributes'], ref_nodeAttributes)
        self.assertEqual(snap_cx[6]['edgeAttributes'], ref_edgeAttributes)
        self.assertEqual(snap_cx[7]['status'], ref_status)

        ref_structure = [
            {'metaData': ref_metaData},
            {'cyTableColumn': ref_cyTableColumn},
            {'networkAttributes': ref_networkAttributes},
            {'nodes': ref_nodes},
            {'edges': ref_edges},
            {'nodeAttributes': ref_nodeAttributes},
            {'edgeAttributes': ref_edgeAttributes},
            {'status': ref_status}]
        self.assertEqual(snap_cx, ref_structure)

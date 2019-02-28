#!/usr/bin/env python3

import unittest
from KaSaAn.core import KappaAgent, KappaToken, KappaRule


class TestKappaRule(unittest.TestCase):
    """Testing various aspects of a Kappa rule representation."""
    def test_string_representation(self):
        self.assertTrue(str(KappaRule("Bob(s1[./1] s2{a/b} s3{=0/+=1}), Jane(s1[./1] s2[2/.]), Jane(s2[2/.] s3[./3]), Jane(s3[./3]), Bob(s3{=3})-, Jane()+ | 1 Mary, -1 John, -1 Luke @ 'a' * 'b' / ('c' + 'd') {'a' + 'b' / 'd' : 5}")),
                        "Bob(s1[./1]{#} s2[#]{a/b} s3{=0/+=1}), Bob(s3{=3}), Jane(), Jane(s1[./1]{#} s2[2/.]{#}), Jane(s2[2/.]{#} s3[./3]{#}), Jane(s3[./3]{#}) | 1 Mary, -1 John, -1 Luke @ 'a' * 'b' / ('c' + 'd') { 'a' + 'b' / 'd' : 5 }")
        self.assertTrue(str(KappaRule("Bob(s1[./1]), /*comment*/Bob(s1[./1]) @ 1 //comment")),
                        "Bob(s1[./1]{#}), Bob(s1[./1]{#}) @ 1")

    def test_get_name(self):
        self.assertEqual(KappaRule("'11' Bob(s1[./1]), Bob(s1[./1]) @ 1").get_name(), "'11'")
        self.assertEqual(KappaRule("'r1' Bob(s1[./1]), Bob(s1[./1]) @ 1").get_name(), "'r1'")
        self.assertEqual(KappaRule("Bob(s1[./1]), Bob(s1[./1]) @ 1").get_name(), '')

    def test_get_rate_primary(self):
        self.assertEqual(KappaRule("Bob(s2{a/b}, s3{=0}) @ 1").get_rate_primary(), '1')
        self.assertEqual(KappaRule("Bob(s2{a}, s3{=0/+=1}) @ 1.0").get_rate_primary(), '1.0')
        self.assertEqual(KappaRule("Bob(s2{b}, s3{>=1/-=1}) @ 1e5").get_rate_primary(), '1e5')
        self.assertEqual(KappaRule("Bob(s2{b}, s3{>=1/-=1}) @ 1e-5").get_rate_primary(), '1e-5')
        self.assertEqual(KappaRule("Bob(s2{b}, s3{>=1/-=1}) @ 1.0e-5").get_rate_primary(), '1.0e-5')
        self.assertEqual(KappaRule("Bob(s2{b}, s3{>=1/-=1}) @ 'a' + 'b' / 'c' { 1.0e-5}").get_rate_primary(),
                         "'a' + 'b' / 'c'")

    def test_get_rate_unary(self):
        self.assertEqual(KappaRule("Bob(s2{a/b}, s3{=0}) @ 1 {1}").get_rate_unary(), '1')
        self.assertEqual(KappaRule("Bob(s2{a}, s3{=0/+=1}) @ 1.0 {1.0}").get_rate_unary(), '1.0')
        self.assertEqual(KappaRule("Bob(s2{b}, s3{>=1/-=1}) @ 1e5 {1e5}").get_rate_unary(), '1e5')
        self.assertEqual(KappaRule("Bob(s2{b}, s3{>=1/-=1}) @ 1e-5 {1e-5}").get_rate_unary(), '1e-5')
        self.assertEqual(KappaRule("Bob(s2{b}, s3{>=1/-=1}) @ 1.0e-5 {1.0e-5}").get_rate_unary(), '1.0e-5')
        self.assertEqual(KappaRule("Bob(s2{b}, s3{>=1/-=1}) @ 1.0e-5 {'a' + 'b' / 'c'}").get_rate_unary(),
                         "'a' + 'b' / 'c'")

    def test_get_horizon(self):
        self.assertEqual(KappaRule("Bob(s2{b}, s3{>=1/-=1}) @ 1 {99:5}").get_horizon(), 5)
        self.assertEqual(KappaRule("Bob(s2{b}, s3{>=1/-=1}) @ 1 { 'a' : 5 }").get_horizon(), 5)

    def test_get_agents(self):
        self.assertEqual(KappaRule("Bob(s1[./1]), /*comment*/Bob(s1[./1]) @ 1 //comment").get_agents(),
                         [KappaAgent("Bob(s1[./1]{#})"), KappaAgent("Bob(s1[./1]{#})")])
        self.assertEqual(KappaRule("Bob(s1[1/.]), Bob(s1[1/.]) @ 1").get_agents(),
                         [KappaAgent("Bob(s1[1/.]{#})"), KappaAgent("Bob(s1[1/.]{#})")])
        self.assertEqual(KappaRule("Bob(s1[1/.]), Bob(s1[1/2]), Bob(s1[./2]) @ 1").get_agents(),
                         [KappaAgent("Bob(s1[./2]{#})"), KappaAgent("Bob(s1[1/.]{#})"), KappaAgent("Bob(s1[1/2]{#})")])

    def test_get_tokens(self):
        self.assertEqual(KappaRule("| 1 Mary, 1 John, -1 Luke @ 1").get_tokens(),
                         [KappaToken('1 Mary'), KappaToken('1 John'), KappaToken('-1 Luke')])
        self.assertEqual(KappaRule("Bob(s1[./1] s2{a/b} s3{=0/+=1}), Jane(s1[./1] s2[2/.]), Jane(s2[2/.] s3[./3]), Jane(s3[./3]), Bob(s3{=3})-, Jane()+ | 1 Mary, 1 John, -1 Luke @ 'a' * 'b' / ('c' + 'd') {'a' + 'b' / 'd' : 5}").get_tokens(),
                         [KappaToken('1 Mary'), KappaToken('1 John'), KappaToken('-1 Luke')])
        self.assertEqual(KappaRule("Bob()+ @ 'foo'").get_tokens(), [])

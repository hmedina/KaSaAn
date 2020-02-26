#!/usr/bin/env python3

import unittest
from KaSaAn.core import KappaContactMap


class TestKappaContactMap(unittest.TestCase):
    """Text various elements of the parsing and rendering of a KappaContactMap."""
    cm_dedicated = KappaContactMap('./models/contact_map/inputs.ka')

    def test_agent_number(self, cm=cm_dedicated):
        self.assertEqual(len(cm._parsed_kappa.keys()), 4)
        self.assertEqual(len(cm._agent_graphics.keys()), 4)

    def test_agent_names(self, cm=cm_dedicated):
        agent_names = ['Foo', 'Bar', 'Baz', 'Fitz']
        self.assertEqual(list(cm._agent_graphics.keys()), agent_names)

    def test_agent_bind_sites(self, cm=cm_dedicated):
        ref_bind_sites = {'Foo': ['bork'],
                         'Bar': ['stan'],
                         'Baz': ['ge89', 'f856'],
                         'Fitz': ['a', 'fran', 'gif', 'jif']}
        cm_bind_sites = {}
        for agent_name in cm._agent_graphics.keys():
            cm_bind_sites[agent_name] = list(cm._agent_graphics[agent_name]['bnd_sites'].keys())
        self.assertEqual(ref_bind_sites, cm_bind_sites)

    def test_agent_flagpole_sites(self, cm=cm_dedicated):
        ref_fp_sites = {'Foo': ['bork', 'woof', 'miau', 'hehehe', 'huehuehue'],
                        'Bar': ['stan'],
                        'Baz': ['p25'],
                        'Fitz': []}
        cm_fp_sites = {}
        for agent_name in cm._agent_graphics.keys():
            cm_fp_sites[agent_name] = list(cm._agent_graphics[agent_name]['flagpole_sites'].keys())
        self.assertEqual(ref_fp_sites, cm_fp_sites)

    def test_bond_number(self, cm=cm_dedicated):
        self.assertEqual(len(cm._bond_types.keys()), 6)

    def test_binding_site_number(self, cm=cm_dedicated):
        bind_site_num = 0
        for agent_name in cm._agent_graphics.keys():
            bind_site_num += len(cm._agent_graphics[agent_name]['bnd_sites'])
        self.assertEqual(bind_site_num, 8)

    def test_flagpole_site_number(self, cm=cm_dedicated):
        flagpole_site_num = 0
        for agent_name in cm._agent_graphics.keys():
            flagpole_site_num += len(cm._agent_graphics[agent_name]['flagpole_sites'])
        self.assertEqual(flagpole_site_num, 7)

#! /usr/bin/env python3
"""Contains the parent class to `KappaSnapshot` and `KappaComplex`, with shared methods."""

from abc import abstractmethod
from typing import List, Dict, Optional
import matplotlib.colors as mpco
import networkx as nx
import xml.etree.ElementTree as ET

from .KappaAgent import KappaAgent
from .KappaBond import KappaBond
from .KappaEntity import KappaEntity


class KappaMultiAgentGraph(KappaEntity):
    """Abstract class containing common components to `KappaComplex` and `KappaSnapshot`, its subclasses."""

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def to_networkx(self) -> nx.MultiGraph:
        """Abstract method included as place-holder for typing reasons."""
        pass

    def _kappa_to_cytoscape_cx(self) -> List[Dict]:
        """
        Given a kappa graph (i.e. KappaComplex or KappaSnapshot), produce a Python structure
         that can be JSON encoded to produce a Cytoscape-compatible CX file.
        """
        kappa_net = self.to_networkx()
        # construct "node" and "nodeAttributes" structures
        cx_nodes = []
        cx_node_attributes = []
        for node_ident, node_data in kappa_net.nodes.data():
            cx_node = {'@id': node_ident,
                       'n': node_data['kappa'].get_agent_name()}
            cx_node_attribute = {'po': node_ident,
                                 'n': 'raw_expression',
                                 'v': str(node_data['kappa'])}
            cx_nodes.append(cx_node)
            cx_node_attributes.append(cx_node_attribute)
        # cytoscape expects edges to have identifiers; these exist in the same space as the nodes;
        # I preserve node identifiers, and start a counter from those to then identify edges
        edge_ident = 0 + kappa_net.number_of_nodes()
        cx_edges = []
        cx_edge_attributes = []
        for e_source, e_target, e_data in kappa_net.edges.data():
            # find the port names
            port_names = []
            e_source_kappa = kappa_net.nodes.data()[e_source]['kappa']
            e_target_kappa = kappa_net.nodes.data()[e_target]['kappa']
            bond_type: KappaBond = e_data['bond type']
            for this_agent in [e_source_kappa, e_target_kappa]:
                for this_site in this_agent.get_agent_signature():
                    # is this site a port, or a counter?
                    if this_site.get_port_bond_state():
                        if e_data['bond id'] == this_site.get_port_bond_state():
                            port_names.append(this_site.get_port_name())
            # build edge dictionary list
            cx_edge = {'s': e_source,
                       't': e_target,
                       '@id': edge_ident}
            cx_edge_attribute = [{'po': edge_ident,
                                  'n': 'bond_type',
                                  'v': str(bond_type)},
                                 {'po': edge_ident,
                                  'n': 's_agent_type',
                                  'v': e_source_kappa.get_agent_name()},
                                 {'po': edge_ident,
                                  'n': 't_agent_type',
                                  'v': e_target_kappa.get_agent_name()},
                                 {'po': edge_ident,
                                  'n': 's_port_name',
                                  'v': port_names[0]},
                                 {'po': edge_ident,
                                  'n': 't_port_name',
                                  'v': port_names[1]},
                                 {'po': edge_ident,
                                  'n': 'ident_in_snap',
                                  'v': e_data['bond id']}]
            cx_edges.append(cx_edge)
            cx_edge_attributes.extend(cx_edge_attribute)
            edge_ident += 1
        # build cytoscape table structure
        cx_table_columns = [{'applies_to': 'node_table', 'n': 'name'},
                            {'applies_to': 'node_table', 'n': 'raw_expression'},
                            {'applies_to': 'edge_table', 'n': 'name'},
                            {'applies_to': 'edge_table', 'n': 'bond_type'},
                            {'applies_to': 'edge_table', 'n': 's_agent_type'},
                            {'applies_to': 'edge_table', 'n': 't_agent_type'},
                            {'applies_to': 'edge_table', 'n': 's_port_name'},
                            {'applies_to': 'edge_table', 'n': 't_port_name'},
                            {'applies_to': 'edge_table', 'n': 'ident_in_snap'},
                            {'applies_to': 'network_table', 'n': 'name'}]
        # build cytoscape metadata structure
        cx_metadata = [{'name': 'nodes', 'version': '1.0'},
                       {'name': 'nodeAttributes', 'version': '1.0'},
                       {'name': 'edges', 'version': '1.0'},
                       {'name': 'edgeAttributes', 'version': '1.0'},
                       {'name': 'cyTablecolumn', 'version': '1.0'},
                       {'name': 'networkAttributes', 'version': '1.0'}]
        # build cytoscape status structure; unclear why it is needed
        cx_status = [{'error': '', 'success': True}]
        # pack and return
        cx_data = [
            {'metaData': cx_metadata},
            {'cyTableColumn': cx_table_columns},
            {'nodes': cx_nodes},
            {'edges': cx_edges},
            {'nodeAttributes': cx_node_attributes},
            {'edgeAttributes': cx_edge_attributes},
            {'status': cx_status}
        ]
        return cx_data

    def _kappa_to_graphml(self, node_coloring: Optional[Dict[KappaAgent, any]] = None) -> ET.ElementTree:
        """Builds the a GraphML representation, ultimately exported as an XML file.
         This method relies on `self.to_netowrkx()`, which is realized for KappaSnapshot
         and KappaComplex objects.
         Optional argument `node_coloring` colorizes by single-agent patterns."""
        
        def _colorize_for_node(node_kappa) -> str:
            """Deal with agent color: ideally one, possibly multiple, maybe none"""
            if node_coloring is not None:
                match_colors = [k_col for k_exp, k_col in node_coloring.items() if k_exp in node_kappa]
                if len(match_colors) > 0:
                    chosen_color = match_colors[0]
                    if isinstance(chosen_color, str):
                        return chosen_color
                    elif mpco.is_color_like(chosen_color):
                        return mpco.to_hex(chosen_color)
                    else:
                        Warning("I don't know how to serialize type {} of {}, returning empty string".format(type(chosen_color), chosen_color))
                        return ''

        graphml_root = ET.Element('graphml', attrib={
            'xmlns': "http://graphml.graphdrawing.org/xmlns",
            'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
            'xsi:schemaLocation': "http://graphml.graphdrawing.org/xmlns " +
            "http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd"})
        tree = ET.ElementTree(graphml_root)

        # define & add attributes for typing & naming & identifying agents & bonds
        data_keys = [
            ('node', 'AgentType', 'string'),
            ('node', 'AgentExpression', 'string'),
            ('node', 'AgentIdentifier', 'int'),
            ('node', 'NodeColor', 'string'),
            ('edge', 'BondType', 'string'),
            ('edge', 'LocalIdentifier', 'int')
        ]
        for key_domain, key_id, key_type in data_keys:
            tree.getroot().append(ET.Element('key', attrib={
                'for': key_domain, 'id': key_id, 'attr.name': key_id, 'attr.type': key_type
            }))

        this_net = self.to_networkx()
        max_degree = len(nx.degree_histogram(this_net))

        # define & add graph sub-tree, with meta-data for efficient parsing
        tree.getroot().append(ET.Element('graph', attrib={
            'id': 'G',
            'edgedefault': 'undirected',
            'parse.nodeids': 'canonical',
            'parse.edgeids': 'canonical',
            'parse.order': 'nodesfirst',
            'parse.maxindegree': str(max_degree),
            'parse.maxoutdegree': str(max_degree),
            'parse.nodes': str(this_net.order()),
            'parse.edges': str(this_net.size(weight=None))
        }))
        graph_root = tree.find('./graph')

        # node iteration
        for n_id, n_data in this_net.nodes.items():
            n_degree = this_net.degree(n_id)
            new_node = ET.Element('node', attrib={'id': 'n{}'.format(n_id), 'parse.indegree': str(n_degree), 'parse.outdegree': str(n_degree)})
            
            # metadata for nodes
            node_meta = [
                ('desc', None, n_data['kappa']),
                ('data', 'AgentType', n_data['kappa'].get_agent_name()),
                ('data', 'AgentExpression', n_data['kappa']),
                ('data', 'AgentIdentifier', n_id),
                ('data', 'NodeColor', _colorize_for_node(n_data['kappa']))
            ]
            for n_class, key_name, payload in node_meta:
                node_annot = ET.Element(n_class) if key_name is None else ET.Element(n_class, attrib={'key': key_name})
                node_annot.text = str(payload)
                new_node.append(node_annot)
            graph_root.append(new_node)

            # generate ports from KappaPorts
            for some_ix, some_site in enumerate(n_data['kappa'].get_agent_ports()):
                # type NMTOKEN is more constrained than Kappa's Unicode,
                # so the "name", which serves as an identifier, is just the index in the agent's signature
                new_port = ET.Element('port', attrib={'name': str(some_ix)})
                port_desc = ET.SubElement(new_port, 'desc')
                port_desc.text = str(some_site)
                new_node.append(new_port)
        
        # edge iteration
        edge_counter = 0    # non-id'd graphs do not have global edge identifiers
        for e_source, e_target, e_data in this_net.edges(data=True):
            port_ix_source = this_net.nodes[e_source]['kappa'].get_agent_ports().index(this_net.nodes[e_source]['kappa'].get_port(e_data['bond type'].site_one))
            port_ix_target = this_net.nodes[e_target]['kappa'].get_agent_ports().index(this_net.nodes[e_target]['kappa'].get_port(e_data['bond type'].site_two))
            new_edge = ET.Element('edge', attrib={
                'id': 'edge{}'.format(edge_counter),
                'directed': 'false',
                'source': 'n{}'.format(e_source),
                'target': 'n{}'.format(e_target),
                'sourceport': str(port_ix_source),
                'targetport': str(port_ix_target)
            })
            graph_root.append(new_edge)
            # metadata for edges
            edge_meta = [
                ('BondType', e_data['bond type']),
                ('LocalIdentifier', e_data['bond id'])
            ]
            for key_name, payload in edge_meta:
                edge_annot = ET.Element('data', attrib={'key': key_name})
                edge_annot.text = str(payload)
                new_edge.append(edge_annot)
            edge_counter += 1
        return tree

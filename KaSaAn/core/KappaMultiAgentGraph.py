#! /usr/bin/env python3
"""Contains the parent class to `KappaSnapshot` and `KappaComplex`, with shared methods."""

from abc import abstractmethod
from typing import List, Dict, Optional
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

        graphml_root = ET.Element('graphml', attrib={
            'xmlns': "http://graphml.graphdrawing.org/xmlns",
            'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
            'xsi:schemaLocation': "http://graphml.graphdrawing.org/xmlns " +
            "http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd"})
        tree = ET.ElementTree(graphml_root)

        # define & add attributes for typing & naming & identifying agents
        attr_node_name = ET.SubElement(tree.getroot(), 'key')
        attr_node_name.set('for', 'node')
        attr_node_name.set('id', 'AgentType')
        attr_node_name.set('attr.name', 'AgentType')
        attr_node_name.set('attr.type', 'string')
        attr_node_expr = ET.SubElement(tree.getroot(), 'key')
        attr_node_expr.set('for', 'node')
        attr_node_expr.set('id', 'AgentExpression')
        attr_node_expr.set('attr.name', 'AgentExpression')
        attr_node_expr.set('attr.type', 'string')
        attr_node_ident = ET.SubElement(tree.getroot(), 'key')
        attr_node_ident.set('for', 'node')
        attr_node_ident.set('id', 'AgentIdentifier')
        attr_node_ident.set('attr.name', 'AgentIdentifier')
        attr_node_ident.set('attr.type', 'int')
        attr_node_color = ET.SubElement(tree.getroot(), 'key')
        attr_node_color.set('for', 'node')
        attr_node_color.set('id', 'NodeColor')
        attr_node_color.set('attr.name', 'color')
        attr_node_color.set('attr.type', 'string')
        # define & add attributes for typing bonds
        attr_bond_type = ET.SubElement(tree.getroot(), 'key')
        attr_bond_type.set('for', 'edge')
        attr_bond_type.set('id', 'BondType')
        attr_bond_type.set('attr.name', 'BondType')
        attr_bond_type.set('attr.type', 'string')
        attr_bond_local_id = ET.SubElement(tree.getroot(), 'key')
        attr_bond_local_id.set('for', 'edge')
        attr_bond_local_id.set('id', 'LocalIdentifier')
        attr_bond_local_id.set('attr.name', 'LocalIdentifier')
        attr_bond_local_id.set('attr.type', 'int')
        # define & add graph sub-tree
        graph_root = ET.SubElement(tree.getroot(), 'graph')
        graph_root.set('id', 'G')
        graph_root.set('edgedefault', 'undirected')
        graph_root.set('parse.nodeids', 'canonical')
        graph_root.set('parse.edgeids', 'canonical')
        graph_root.set('parse.order', 'nodesfirst')

        this_net = self.to_networkx()
        # annotations for eficient parsing: parse.maxindegree & parse.maxoutdegree & parse.nodes & parse.edges
        max_degree = len(nx.degree_histogram(this_net))
        graph_root.set('parse.maxindegree', str(max_degree))
        graph_root.set('parse.maxoutdegree', str(max_degree))
        graph_root.set('parse.nodes', str(this_net.order()))
        graph_root.set('parse.edges', str(this_net.size(weight=None)))
        # node iteration
        for n_id, n_data in this_net.nodes.items():
            new_node = ET.SubElement(graph_root, 'node')
            new_node.set('id', 'n{}'.format(n_id))
            n_degree = this_net.degree(n_id)
            new_node.set('parse.indegree', str(n_degree))
            new_node.set('parse.outdegree', str(n_degree))
            # set element with kappa expression as description
            node_desc = ET.SubElement(new_node, 'desc')
            node_desc.text = str(n_data['kappa'])
            # set element with AgentType
            node_data_name = ET.SubElement(new_node, 'data')
            node_data_name.set('key', 'AgentType')
            node_data_name.text = n_data['kappa'].get_agent_name()
            # set element with AgentExpression
            node_data_expr = ET.SubElement(new_node, 'data')
            node_data_expr.set('key', 'AgentExpression')
            node_data_expr.text = str(n_data['kappa'])
            # set element with AgentIdentifier
            node_data_id = ET.SubElement(new_node, 'data')
            node_data_id.set('key', 'AgentIdentifier')
            node_data_id.text = str(n_id)
            # If there is a color eligible from the supplied scheme,
            # use the first one.
            if node_coloring is not None:
                match_colors = [k_col for k_exp, k_col in node_coloring.items() if k_exp in n_data['kappa']]
                if len(match_colors) > 0:
                    node_data_color = ET.SubElement(new_node, 'data')
                    node_data_color.set('key', 'NodeColor')
                    node_data_color.text = match_colors[0]
            for some_site in n_data['kappa'].get_agent_signature():
                new_port = ET.SubElement(new_node, 'port')
                new_port.set('name', some_site.name)
        # edge iteration
        edge_counter = 0    # non-id'd graphs do not have global edge identifiers
        for e_source, e_target, e_data in this_net.edges(data=True):
            new_edge = ET.SubElement(graph_root, 'edge')
            new_edge.set('id', 'edge{}'.format(edge_counter))
            new_edge.set('directed', 'false')
            new_edge.set('source', 'n{}'.format(e_source))
            new_edge.set('target', 'n{}'.format(e_target))
            new_edge.set('sourceport', e_data['bond type'].site_one)    # this works because kappa bonds
            new_edge.set('targetport', e_data['bond type'].site_two)    # are oriented, ergo ordered
            # set element with BondType
            new_bond_type = ET.SubElement(new_edge, 'data')
            new_bond_type.set('key', 'BondType')
            new_bond_type.text = str(e_data['bond type'])
            # set element with LocalIdentifier
            new_bond_id = ET.SubElement(new_edge, 'data')
            new_bond_id.set('key', 'LocalIdentifier')
            new_bond_id.text = e_data['bond id']
            edge_counter += 1
        return tree

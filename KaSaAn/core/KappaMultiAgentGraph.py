#! /usr/bin/env python3

from abc import abstractmethod
from typing import List, Dict

from .KappaEntity import KappaEntity


class KappaMultiAgentGraph(KappaEntity):
    """Abstract class containing common components to `KappaComplex` and `KappaSnapshot`, its subclasses."""

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def to_networkx(self):
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

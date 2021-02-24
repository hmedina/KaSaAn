#!/usr/bin/env python3

import networkx as nx
import numpy as np
from collections import deque
from typing import Deque, List, Tuple, Set, Union
from .KappaBond import KappaBond
from .KappaComplex import KappaComplex
from .KappaSite import KappaPort


"""
def complex_in_complex(kappa_query: KappaComplex, kappa_target: KappaComplex) -> int:
    Routine to compute the number of embeddings a query graph has into a host graph.

    # litany of short circuits: target too small
    if kappa_query.get_size_of_complex() > kappa_target.get_size_of_complex():
        return 0
    # litany of short circuits: target too small, on edges
    if kappa_query.get_number_of_bonds() > kappa_target.get_number_of_bonds():
        return 0
    # litany of short circuits: sum formula (aka composition)
    query_composition = kappa_query.get_complex_composition()
    target_composition = kappa_target.get_complex_composition()
    for agent_type, query_abundance in query_composition.items():
        if agent_type not in target_composition:
            return 0
        if target_composition[agent_type] < query_abundance:
            return 0

    #
    # ToDo: litany of short circuits: bond types
    #

    query_net = kappa_query.to_networkx()
    target_net = kappa_target.to_networkx()
    # embark on traversal; success means an embedding was found
    found_embeddings = 0

    #
    # ToDo: define least abundant agent types as node starts
    #
"""


def number_of_embeddings(ka_query: KappaComplex, ka_target: KappaComplex) -> int:
    """Calculates the number of embeddings of ka_query into ka_target."""
    ka_target


def _traverse(query_net: nx.MultiGraph, target_net: nx.MultiGraph, query_start: int, target_start: int) -> bool:
    """Attempt a traversal of target_net, starting at target_start, matched to query_start, following query_net's
    topology."""
    # stack of node identifiers, integers from the networkx representation
    node_stack: Deque[Tuple[int, Union[int, None], int]] = deque()
    node_stack.append((query_start, None, target_start))
    nodes_visited: Set[int] = set()
    while node_stack:
        q_node, q_prev, t_node = node_stack.pop()
        if q_node not in nodes_visited:
            # update t_node according to what got us from q_prev to q_node
            if q_prev is not None:
                # uniqueness of site name per agent guarantees a bond type can appear at most once in an agent's
                # bond set; this yields "rigidity" to the matcher
                transforming_bond_type: KappaBond = query_net.get_edge_data(q_prev, q_node)[0]['bond type']
                target_transforming_bond_index: int = \
                    np.where([transforming_bond_type == item for item in
                              [target_net.get_edge_data(a, b)[0]['bond type']
                               for a, b in nx.edges(target_net, t_node)]])[0][0]
                t_node = list(nx.edges(target_net, t_node))[target_transforming_bond_index][1]
            # now at parity, match by node & edge data
            node_matched = _node_match(query_net, target_net, q_node, t_node)
            edge_matched = _edge_match(query_net, target_net, q_node, t_node)
            if node_matched and edge_matched:
                nodes_visited.add(q_node)
                for q_neighbor in nx.neighbors(query_net, q_node):
                    node_stack.append((q_neighbor, q_node, t_node))
            else:
                return False
    return True


def _node_match(query_net: nx.MultiGraph, target_net: nx.MultiGraph, query_node: int, target_node: int) -> bool:
    """Special purpose matcher that ignores bond types, it only considers if sites are bound."""
    match: bool = False
    query = query_net.nodes[query_node]['kappa']
    target = target_net.nodes[target_node]['kappa']
    for site in query.get_agent_ports():
        s_name = site.get_port_name()
        s_stat = '{' + site.get_port_int_state() + '}'
        s_bond = '[' + site.get_port_bond_state() + ']' if site.get_port_bond_state() in ['.', '_', '#'] else '[_]'
        relaxed_port = KappaPort(s_name + s_bond + s_stat)
        if not any([relaxed_port in t_site for t_site in target.get_agent_ports()]):
            return match
    match = True
    return match


def _edge_match(query_net: nx.MultiGraph, target_net: nx.MultiGraph, query_node: int, target_node: int) -> bool:
    """Special purpose matcher that only compares bond types. Returns a tuple, where the first value is a boolean
    holding whether the whole thing matched, and the second the list of neighbors in target for which there was a
    bond-type match."""
    match: bool = False
    query_edges = nx.edges(query_net, query_node)
    query_bond_types: List[KappaBond] = [query_net.get_edge_data(a, b)[0]['bond type'] for a, b in query_edges]
    target_edges = list(nx.edges(target_net, target_node))
    target_bond_types: List[KappaBond] = [target_net.get_edge_data(a, b)[0]['bond type'] for a, b in target_edges]
    for query_bond_type in query_bond_types:
        if not any([query_bond_type == target_bond_type for target_bond_type in target_bond_types]):
            return match
    match = True
    return match


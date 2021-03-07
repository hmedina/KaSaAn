#!/usr/bin/env python3
"""Contains `KappaComplex`, a class to represents a list of agents chained into a larger entity, and the `embed_and_map`
function."""

import re
import networkx as nx
import numpy as np
from collections import deque
from typing import Deque, Dict, List, FrozenSet, Set, Tuple, Union

from .KappaMultiAgentGraph import KappaMultiAgentGraph
from .KappaAgent import KappaAgent
from .KappaBond import KappaBond
from .KappaError import ComplexParseError, AgentParseError
from .KappaSite import KappaPort


class KappaComplex(KappaMultiAgentGraph):
    """Class for representing Kappa complexes. E.g. `A(b[1] s{u}[.]), B(a[1] c[2]), C(b[2] a[3]), A(c[3] s[.]{x})`."""

    # define agent pattern
    _agent_idnt_pat = r'(?:x\d+:)?'
    _agent_name_pat = r'(?:[_~][a-zA-Z0-9_~+-]+|[a-zA-Z][a-zA-Z0-9_~+-]*)'
    _agent_sign_pat = r'\([^()]*\)'
    _agent_pat = _agent_idnt_pat + _agent_name_pat + _agent_sign_pat
    _agent_pat_re = re.compile(_agent_pat)

    def __init__(self, expression: str):
        self._raw_expression: str
        self._agents: List[KappaAgent]
        self._agent_identifiers: List[int]
        self._agent_types: Set[KappaAgent]
        self._kappa_expression: str
        self._composition: Dict[KappaAgent, int]

        self._raw_expression = expression
        # get the set of agents making up this complex
        matches = self._agent_pat_re.findall(expression.strip())
        if len(matches) == 0:
            raise ComplexParseError('Complex <' + self._raw_expression + '> appears to have zero agents.')
        try:
            agent_list = []
            agent_idents = []
            agent_types = set()
            composition = {}
            for item in matches:
                agent = KappaAgent(item)
                agent_list.append(agent)
                if agent.get_agent_identifier() is not None:
                    agent_idents.append(agent.get_agent_identifier())
                agent_type = KappaAgent(agent.get_agent_name() + '()')
                agent_types.update([agent_type])
                if agent_type in composition:
                    composition[agent_type] += 1
                else:
                    composition[agent_type] = 1
        except AgentParseError as a:
            raise ComplexParseError('Could not parse agents in complex <' + expression + '>.') from a
        self._agents = sorted(agent_list)
        self._agent_identifiers = agent_idents
        self._agent_types = agent_types
        self._composition = dict(sorted(composition.items(), key=lambda item: item[1]))
        # canonicalize the kappa expression
        self._kappa_expression = ', '.join([str(agent) for agent in self._agents])

    def get_number_of_bonds(self) -> int:
        """Returns the number of bonds in the complex."""
        bonds = set()
        for agent in self._agents:
            bonds.update(agent.get_bond_identifiers())
        return len(bonds)

    def get_size_of_complex(self) -> int:
        """Returns the size, in agents, of this complex."""
        return len(self._agents)

    def get_agent_types(self) -> Set[KappaAgent]:
        """Returns the set of agent names (or agent types) that make up the complex."""
        return self._agent_types

    def get_all_agents(self) -> List[KappaAgent]:
        """Returns a list of KappaAgents, filled with agents plus their signatures, present in this complex."""
        # replace commas with spaces, then split string into a list at closing parenthesis
        return self._agents

    def get_complex_composition(self) -> Dict[KappaAgent, int]:
        """Returns a dictionary where the key is an agent (fully qualified, not just a name), and the value the number of times that agent appears in this complex."""
        return self._composition

    def get_number_of_embeddings_of_agent(self, query) -> int:
        """Returns the number of embeddings the query agent has on the KappaComplex."""
        # type the query into an Agent, if it's not one already
        if not type(query) is KappaAgent:
            q_agent = KappaAgent(query)
        else:
            q_agent = query
        # iterate over agents, checking if query is in each agent
        match_number = 0
        for s_agent in self._agents:
            if q_agent in s_agent:
                match_number += 1
        return match_number

    def get_number_of_embeddings_of_complex(self, query, symmetry_adjust: bool = True) -> int:
        """Returns the number of embedding the query complex has on the KappaComplex. Optional parameter to not perform
        the symmetry adjustment and report number of raw embeddings, without dividing by the number of symmetries 
        preserved in the query complex's image in the target."""
        if not type(query) is KappaComplex:
            q_complex = KappaComplex(query)
        else:
            q_complex = query
        total_maps, unique_maps = embed_and_map(q_complex, self)
        if symmetry_adjust:
            return len(unique_maps)
        else:
            return len(total_maps)

    def get_number_of_embeddings(self, query) -> int:
        """Wrapper for the two specialized functions, for agent and complex."""
        if type(query) is KappaAgent:
            return self.get_number_of_embeddings_of_agent(query)
        elif type(query) is KappaComplex:
            return self.get_number_of_embeddings_of_complex(query)
        else:
            try:
                try:
                    return self.get_number_of_embeddings_of_agent(KappaAgent(query))
                except AgentParseError:
                    return self.get_number_of_embeddings_of_complex(KappaComplex(query))
            except ComplexParseError:
                raise ValueError('Could not parse query as a KappaAgent nor as a KappaComplex.')

    def get_agent_identifiers(self) -> List[int]:
        """Returns a list with the numeric agent identifiers, if any."""
        return self._agent_identifiers

    def to_networkx(self, identifier_offset: int = 0) -> nx.MultiGraph:
        """Returns a Multigraph representation of the complex, abstracting away binding site data. Nodes represent
        agents, edges their bonds. Nodes have an attribute dictionary where the key `kappa` holds the KappaAgent.
        Edges have an attribute dictionary where the key `bond id` holds the bond identifier from the Kappa expression.
        Node identifiers are integers, using the order of agent declaration. For a graph `g`, `g.nodes.data()` displays the
        node identifiers and their corresponding `KappaAgents`, and `g.edges.data()` displays the edges, using the node
        identifiers as well as the kappa identifiers.
        The optional parameter `identifier_offset` will offset all numeric identifiers reported; used in unlabeled snapshots, or when combining graphs."""
        kappa_complex_multigraph = nx.MultiGraph()
        dangle_bond_dict = {}                       # store unpaired bonds he
        paired_bond_list = []                       # store tuples of (agent index 1, agent index 2, bond identifier)
        agent_counter = 0                           # if using un-labeled kappa, default to this
        for agent in self.get_all_agents():
            if agent.get_agent_identifier():
                agent_global_id = agent.get_agent_identifier() + identifier_offset
            else:
                agent_global_id = agent_counter + identifier_offset
            kappa_complex_multigraph.add_node(agent_global_id, kappa=agent)
            for bond in agent.get_bond_identifiers():
                # if we've already seen this edge and it is in the dangling list, it's partner has already been matched,
                # so we can add this terminus to the bond database and delete from the dangle list
                if bond in dangle_bond_dict:
                    # special case for self-bonds: the first pass already got the alphabetically lower terminus,
                    # so this pass should get the second terminus of the bond
                    if len(agent.get_terminii_of_bond(bond)) > 1:
                        second_terminus = agent.get_terminii_of_bond(bond)[1]
                    else:
                        second_terminus = agent.get_terminii_of_bond(bond)[0]
                    paired_bond_list.append((dangle_bond_dict[bond]['agent id'], agent_global_id,
                                             {'bond id': bond, 'bond type':
                                             KappaBond(agent_one=dangle_bond_dict[bond]['agent name'],
                                                       site_one=dangle_bond_dict[bond]['site name'],
                                                       agent_two=agent.get_agent_name(),
                                                       site_two=second_terminus
                                                       )}))
                    del dangle_bond_dict[bond]
                else:
                    dangle_bond_dict[bond] = {'agent id': agent_global_id,
                                              'agent name': agent.get_agent_name(),
                                              'site name': agent.get_terminii_of_bond(bond)[0]}
            agent_counter += 1
        # if anything remains in the dangling bond list, it means we failed to pair at least one bond terminus
        if dangle_bond_dict:
            raise ValueError('Dangling bonds <' + ','.join(dangle_bond_dict.keys()) +
                             '> found in complex: ' + self._raw_expression)
        kappa_complex_multigraph.add_edges_from(paired_bond_list)
        return kappa_complex_multigraph

    def to_cytoscape_cx(self) -> List[Dict]:
        """
        Export to a structure that, via some json encoding and dumping, can be read by Cytoscape as a CX file. Usage:
        >>> my_cx = my_complex.to_cytoscape_cx()
        >>> with open('my_cx.cx', 'w') as out_file:
        json.dump(my_cx, out_file)
        """
        cx_data = self._kappa_to_cytoscape_cx()
        cx_network_attributes = [{'n': 'name', 'v': 'network'}]
        cx_data.insert(2, {'networkAttributes': cx_network_attributes})
        return cx_data


def embed_and_map(ka_query: KappaComplex, ka_target: KappaComplex) -> \
        Tuple[List[List[Tuple[int, int]]], List[List[Tuple[int, int]]]]:
    """
    Calculates all the embeddings of `ka_query` into `ka_target`, returning both the map of all embeddings, as well as
    the map of embeddings corrected for the number of preserved automorphisms. For a rotational symmetry:
    >>> from KaSaAn.core.KappaComplex import embed_and_map, KappaComplex
    >>> my_comp = KappaComplex('Bob(h[10], t[11]), Bob(h[11], t[12]), Bob(h[12], t[10])')
    >>> maps_all, maps_unique = embed_and_map(my_comp, my_comp)
    >>> maps_all
    [[(0, 0), (2, 2), (1, 1)], [(0, 1), (2, 0), (1, 2)], [(0, 2), (2, 1), (1, 0)]]
    >>> maps_unique
    [[(0, 0), (2, 2), (1, 1)]]
    """
    # litany of short circuits
    if ka_query.get_size_of_complex() > ka_target.get_size_of_complex():    # not enough agents
        return ([], [])
    if ka_query.get_number_of_bonds() > ka_target.get_number_of_bonds():    # not enough bonds
        return ([], [])
    query_comp = ka_query.get_complex_composition()
    target_comp = ka_target.get_complex_composition()
    if not set(query_comp) <= set(target_comp):                             # query agent(s) not present in target
        return ([], [])
    for agent_type, query_abundance in query_comp.items():
        if agent_type not in target_comp:                                   # query agent missing in target
            return ([], [])
        if target_comp[agent_type] < query_abundance:                       # target sum formula too small
            return ([], [])
    # start from the least abundant type, get their node indexes in query network and target network
    # from the <<query is improper subset of target>> check above, all of query's are in target, so query's minimum
    # happens to also be the common minimum
    common_min: KappaAgent = next(iter(query_comp))
    query_network = ka_query.to_networkx()
    target_network = ka_target.to_networkx()
    if not nx.is_connected(query_network):
        raise ValueError('Error: query is not a connected graph.')
    if not nx.is_connected(target_network):
        raise ValueError('Error: target is not a connected graph.')
    # get node identifiers whose agent type is of the common_min
    common_min_q: np.array = np.where([
        common_min in ka_agent for ka_agent in [
            query_network.nodes()[item]['kappa'] for item in query_network.nodes()]])[0]
    common_min_t: np.array = np.where([
        common_min in ka_agent for ka_agent in [
            target_network.nodes()[item]['kappa'] for item in target_network.nodes()]])[0]
    # embark on systematic traversal
    query_start_node = common_min_q[0]
    maps_all: List[List[Tuple[int, int]]] = []
    maps_distinct:  List[List[Tuple[int, int]]] = []
    map_set: Set[FrozenSet[int]] = set()
    for target_start_node in common_min_t:
        map_found = _traverse_from(query_network, target_network, query_start_node, target_start_node)
        if map_found:
            maps_all.append(map_found)
            q_nodes, t_nodes = zip(*map_found)
            t_nodes = frozenset(t_nodes)
            if t_nodes not in map_set:
                map_set.update([t_nodes])
                maps_distinct.append(map_found)
    return maps_all, maps_distinct


def _traverse_from(query_net: nx.MultiGraph, target_net: nx.MultiGraph, query_start: int, target_start: int) -> \
        List[Tuple[int, int]]:
    """Attempt a traversal of `target_net`, starting at `target_start`, matched to `query_start`, following `query_net`'s
    topology. If successful, returns the network mapping: a list of `(q,t)`, the indexes in the query and target
    networks respectively."""
    # stack of node identifiers, integers from the networkx representation
    node_stack: Deque[Tuple[int, Union[int, None], int]] = deque()
    node_stack.append((query_start, None, target_start))
    nodes_visited: Set[int] = set()
    network_map = []
    while node_stack:
        q_node, q_prev, t_node = node_stack.pop()
        if q_node not in nodes_visited:
            # update t_node according to what got us from q_prev to q_node
            if q_prev is not None:
                # uniqueness of site name per agent, plus orientation of bond types,
                # guarantee a bond type can appear at most once in an agent's
                # bond set when read with the right orientation; this yields "rigidity" to the matcher
                transforming_bond_type: KappaBond = query_net.get_edge_data(q_prev, q_node)[0]['bond type']
                if q_prev > q_node:
                    transforming_bond_type = transforming_bond_type.reverse()
                target_bonds: List[KappaBond] = []
                # get oriented bond list, incident on target node
                for a, b in nx.edges(target_net, t_node):
                    bond_type: KappaBond = target_net.get_edge_data(a, b)[0]['bond type']
                    if a < b:
                        target_bonds.append(bond_type)
                    else:
                        target_bonds.append(bond_type.reverse())
                target_transforming_bond_index: int = \
                    np.where([transforming_bond_type == item for item in target_bonds])[0][0]
                t_node = list(nx.edges(target_net, t_node))[target_transforming_bond_index][1]
            # now at parity, match by node & edge data
            node_matched = _node_match(query_net, target_net, q_node, t_node)
            edge_matched = _edge_match(query_net, target_net, q_node, t_node)
            if node_matched and edge_matched:
                network_map.append((q_node, t_node))
                nodes_visited.add(q_node)
                for q_neighbor in nx.neighbors(query_net, q_node):
                    node_stack.append((q_neighbor, q_node, t_node))
            else:
                return []
    return network_map


def _node_match(query_net: nx.MultiGraph, target_net: nx.MultiGraph, query_node: int, target_node: int) -> bool:
    """Special purpose matcher that ignores bond types, considering only if sites are bound. Internal states are matched normally."""
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
    query_bond_types: List[KappaBond] = []
    for a, b in query_edges:
        this_bond: KappaBond = query_net.get_edge_data(a, b)[0]['bond type']
        if a < b:   # if nodes ascending, read bond left-to-right
            query_bond_types.append(this_bond)
        else:
            query_bond_types.append(this_bond.reverse())
    target_edges = list(nx.edges(target_net, target_node))
    target_bond_types: List[KappaBond] = []
    for a, b in target_edges:
        this_bond: KappaBond = target_net.get_edge_data(a, b)[0]['bond type']
        if a < b:   # if nodes ascending, read bond left-to-right
            target_bond_types.append(this_bond)
        else:
            target_bond_types.append(this_bond.reverse())
    for query_bond_type in query_bond_types:
        if not any([query_bond_type == target_bond_type for target_bond_type in target_bond_types]):
            return match
    match = True
    return match

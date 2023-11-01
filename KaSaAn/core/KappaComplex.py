#!/usr/bin/env python3
"""Contains `KappaComplex`, a class to represents a list of agents chained into a larger entity, and the `embed_and_map`
function."""

import xml.etree.ElementTree as ET
import re
import networkx as nx
from pathlib import Path
from collections import deque
from typing import Deque, Dict, List, Set, Tuple, Union

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
        self._agent_by_idents: Dict[int, KappaAgent]
        """Maps an identifier to an Agent; empty if no identifiers present"""
        self._agent_types: Set[KappaAgent]
        self._kappa_expression: str
        self._composition: Dict[KappaAgent, int]
        """Maps an agent type to an abundance"""

        self._raw_expression = expression
        # get the set of agents making up this complex
        matches = self._agent_pat_re.findall(expression.strip())
        if len(matches) == 0:
            raise ComplexParseError('Complex <' + self._raw_expression + '> appears to have zero agents.')
        try:
            agent_list: List[KappaAgent] = []
            agent_idents = []
            agent_types = set()
            composition = {}
            for item in matches:
                agent = KappaAgent(item)
                agent_list.append(agent)
                if agent.get_agent_identifier() is not None:
                    agent_idents.append(agent.get_agent_identifier())
                # update type set, composition structures
                agent_type = KappaAgent(agent.get_agent_name() + '()')
                agent_types.update([agent_type])
                if agent_type in composition:
                    composition[agent_type] += 1
                else:
                    composition[agent_type] = 1
        except AgentParseError as a:
            raise ComplexParseError('Could not parse agents in complex <' + expression + '>.') from a
        self._agents = sorted(agent_list)
        self._agent_types = agent_types
        self._composition = dict(sorted(composition.items(), key=lambda item: item[1]))
        # deal with agent identifier map; 0 is a valid identifier
        if all([isinstance(ag.get_agent_identifier(), int) for ag in agent_list]):
            self._agent_by_idents = {agent.get_agent_identifier(): agent for agent in agent_list}
        elif any([isinstance(ag.get_agent_identifier(), int) for ag in agent_list]):
            Warning('Expression contains identifier for only a subset of agents!\n{}'.format(self._raw_expression))
            self._agent_by_idents = {}
        else:
            self._agent_by_idents = {}
        # canonicalize the kappa expression
        self._kappa_expression = ', '.join([str(agent) for agent in self._agents])

    def get_number_of_bonds(self) -> int:
        """Returns the number of bonds in the complex."""
        bonds = set()
        for agent in self._agents:
            bonds.update(agent.get_bond_identifiers())
        return len(bonds)

    def get_agents_of_bond(self, bond_id: Union[int, str]) -> Union[Tuple[KappaAgent, KappaAgent], None]:
        """Returns a tuple with both KappaAgents on either side of the requested bond identifier, or None if the bond
        is unkown to this complex."""
        if isinstance(bond_id, int):
            bond_id = str(bond_id)
        terminii = []
        for this_agent in self._agents:
            if bond_id in this_agent.get_bond_identifiers():
                terminii.append(this_agent)
        if len(terminii) == 2:
            return terminii
        else:
            return None

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
        """Returns a dictionary where the key is an agent (fully qualified, not just a name), and the value the number
        of times that agent appears in this complex."""
        return self._composition

    def get_number_of_embeddings_of_agent(self, query) -> int:
        """Returns the number of embeddings the query agent has on the KappaComplex. For the 'truth table' of site
        nomenclature, see `KappaPort`."""
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
        """Returns the number of embeddings the query complex has on the KappaComplex. Optional parameter to not perform
        the symmetry adjustment and report number of raw embeddings. See the `embed_and_map` function for examples and
        advanced usage."""
        if not type(query) is KappaComplex:
            q_complex = KappaComplex(query)
        else:
            q_complex = query
        total_maps, unique_maps = embed_and_map(q_complex, self)
        if symmetry_adjust:
            return len(unique_maps)
        else:
            return len(total_maps)

    def get_number_of_embeddings(self, query, symmetry_adjust: bool = True) -> int:
        """Wrapper for the two specialized functions, for agent and complex. Optional parameter to not perform
        the symmetry adjustment and report the number of raw embeddings. See the `embed_and_map` function for examples
        and advanced usage."""
        if type(query) is KappaAgent:
            return self.get_number_of_embeddings_of_agent(query)
        elif type(query) is KappaComplex:
            return self.get_number_of_embeddings_of_complex(query, symmetry_adjust)
        else:
            try:
                try:
                    return self.get_number_of_embeddings_of_agent(KappaAgent(query))
                except AgentParseError:
                    return self.get_number_of_embeddings_of_complex(KappaComplex(query), symmetry_adjust)
            except ComplexParseError:
                raise ValueError('Could not parse <{}> as a KappaAgent nor as a KappaComplex.'.format(query))

    def get_agent_identifiers(self) -> List[int]:
        """Returns a list with the numeric agent identifiers, if any."""
        return self._agent_by_idents.keys()

    def get_agent_from_identifier(self, ident: int) -> Union[KappaAgent, None]:
        """Returns the KappaAgent associated to provided identifier, if any."""
        if ident not in self._agent_by_idents:
            Warning('Returnin None; identifier {} not present in complex\n{}'.format(ident, self._kappa_expression))
            return None
        else:
            return self._agent_by_idents[ident]

    def to_networkx(self, identifier_offset: int = 0) -> nx.MultiGraph:
        """Returns a Multigraph representation of the complex, abstracting away binding site data. Nodes represent
        agents, edges their bonds. Nodes have an attribute dictionary where the key `kappa` holds the KappaAgent.
        Edges have an attribute dictionary where the key `bond id` holds the bond identifier from the Kappa expression.
        Node identifiers are integers, using the order of agent declaration. For a graph `g`, `g.nodes.data()` displays
        the node identifiers and their corresponding `KappaAgents`, and `g.edges.data()` displays the edges, using the
        node identifiers as well as the kappa identifiers.
        The optional parameter `identifier_offset` will offset all numeric identifiers reported; used in unlabeled
        snapshots, or when combining graphs."""
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
                    this_bond_type = KappaBond(agent_one=dangle_bond_dict[bond]['agent name'],
                                               site_one=dangle_bond_dict[bond]['site name'],
                                               agent_two=agent.get_agent_name(),
                                               site_two=second_terminus)
                    paired_bond_list.append((dangle_bond_dict[bond]['agent id'], agent_global_id,
                                             {'bond id': bond, 'bond type': this_bond_type}))
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

    def to_graphml(self, outfile: Union[Path, str, None]) -> ET.ElementTree:
        """Returns an XML ElementTree with a GraphML representation of the complex, using GraphML's ports for
         binding sites. If an output file is given, object is serialized to that file instead."""
        this_tree = self._kappa_to_graphml()
        if outfile is not None:
            ET.indent(this_tree, space='\t')
            this_tree.write(outfile, encoding='UTF-8', xml_declaration=True, method='xml')
        else:
            return this_tree


class NetMap():
    """Class for representing network maps, used for automorphism checking."""

    node_map: Set[Tuple[int, int]]
    """List of tuples, holding the node index of one network that matches the node index in the other."""
    edge_map: Set[Tuple[int, int]]
    """List of tuples, holding the edge index of one network that matches the edge index in the other."""

    def __init__(self):
        self.node_map = set()
        self.edge_map = set()

    def __str__(self) -> str:
        nodes: str = ', '.join(['{} -> {}'.format(a, b) for a, b in self.node_map])
        edges: str = ', '.join(['{} -> {}'.format(a, b) for a, b in self.edge_map])
        return 'Nodes: {}\nEdges: {}'.format(nodes, edges)

    def __eq__(self, other) -> bool:
        return True if self.__hash__() == other.__hash__() else False

    def __hash__(self) -> int:
        origin_n, image_n = zip(*self.node_map)
        if len(self.edge_map) > 0:
            origin_e, image_e = zip(*self.edge_map)
            own_hash = hash(
                (tuple(sorted(origin_n)), tuple(sorted(image_n)), tuple(sorted(origin_e)), tuple(sorted(image_e))))
        else:
            own_hash = hash(
                (tuple(sorted(origin_n)), tuple(sorted(image_n)), None, None))
        return own_hash


def embed_and_map(ka_query: KappaComplex, ka_target: KappaComplex) -> Tuple[List[NetMap], Set[NetMap]]:
    """
    Calculates all the embeddings of `ka_query` into `ka_target`. First element is the list of all mappings,
    while second is the set of automorphism-corrected mappings. For a rotational symmetry:
    >>> from KaSaAn.core.KappaComplex import embed_and_map, KappaComplex
    >>> my_comp = KappaComplex('Bob(h[10], t[11]), Bob(h[11], t[12]), Bob(h[12], t[10])')
    >>> maps_all, maps_unique = embed_and_map(my_comp, my_comp)
    >>> maps_all
    [[(0, 0), (2, 2), (1, 1)], [(0, 1), (2, 0), (1, 2)], [(0, 2), (2, 1), (1, 0)]]
    >>> maps_unique
    [[(0, 0), (2, 2), (1, 1)]]

    There are three ways of satisfying the query in the target, and these rotations inflate the number of "embeddings".
    However, the set of identifiers making up the image of the query in the target is the same for these three:
    `(0, 2, 1)`, `(1, 0, 2)`, and `(2, 1, 0)` are equivalent, and so the target contains only one copy of the query.
    These dual-purpose interpretation of the "embedding" concept yields a function that returns both.
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
    # start from the least abundant type, get their node indexes in query network and target network;
    # from the <<query is improper subset of target>> check above, all of query's are in target by type, so query's
    # minimum must be a type in common; moreover all query's type abundances are equal or greater in target, so if
    # a type is the minimum in query, its abundance will also be either *the*, or just *a*, minimum in target
    common_min: KappaAgent = next(iter(query_comp))
    query_network = ka_query.to_networkx()
    target_network = ka_target.to_networkx()
    if not nx.is_connected(query_network):
        raise ValueError('Error: query is not a connected graph.')
    if not nx.is_connected(target_network):
        raise ValueError('Error: target is not a connected graph.')
    common_min_q: List[int] = []
    for node_id in query_network.nodes:
        if common_min in query_network.nodes[node_id]['kappa']:
            common_min_q.append(node_id)
    common_min_t: List[int] = []
    for node_id in target_network.nodes:
        if common_min in target_network.nodes[node_id]['kappa']:
            common_min_t.append(node_id)
    # embark on systematic traversal
    query_start_node = common_min_q[0]
    maps_all: List[NetMap] = []
    maps_distinct:  Set[NetMap] = set()
    for target_start_node in common_min_t:
        map_found = _traverse_from(query_network, target_network, query_start_node, target_start_node)
        if map_found:
            maps_all.append(map_found)
            maps_distinct.add(map_found)
    return maps_all, maps_distinct


def _traverse_from(query_net: nx.MultiGraph, target_net: nx.MultiGraph, q_start: int, t_start: int) -> NetMap:
    """Attempt a traversal of `target_net`, starting at `target_start`, matched to `query_start`, following
    `query_net`'s topology."""
    HopData = tuple[int, int]
    node_stack: Deque[HopData] = deque()
    node_stack.append(HopData([q_start, t_start]))
    # stack of: query-current, query-previous, transforming-bond, target-current, target-previous
    #  used to traverse the target network, mapping the query-current to the target-current,
    #  and checking if the bond that led from query-previous to query-current would work for
    #  the target network
    nodes_visited: Set[int] = set()
    edges_followed: Set[int] = set()
    network_map = NetMap()
    while node_stack:
        q_node, t_node = node_stack.pop()
        if q_node in nodes_visited:
            node_matched = True             # if we visited this node already, and it got added to the queue,
            edge_matched = True             # it must have passed both of these checks
        else:
            node_matched: bool = _node_match(query_net, target_net, q_node, t_node)
            edge_matched: bool = _edge_match(query_net, target_net, q_node, t_node)
        if node_matched and edge_matched:
            # prepare for next iteration:
            #  add nodes of query, mapped to their images in target, to the node map;
            #  add neighbors of query, mapped to their images in target;
            #  add their respective bonds, mapped to their images in target, to the edge map
            network_map.node_map.add((q_node, t_node))
            nodes_visited.add(q_node)
            for _, q_neighbor, q_data in query_net.edges(q_node, data=True):
                q_type: KappaBond = q_data['bond type'] if q_node < q_neighbor else q_data['bond type'].reverse()
                q_id = int(q_data['bond id'])
                for _, t_neighbor, t_data in target_net.edges(t_node, data=True):
                    t_type: KappaBond = t_data['bond type'] if t_node < t_neighbor else t_data['bond type'].reverse()
                    t_id = int(t_data['bond id'])
                    if q_type == t_type:
                        if q_id not in edges_followed:     # cycle prevention
                            edges_followed.add(q_id)
                            network_map.edge_map.add((q_id, t_id))
                            valid_hop = HopData([q_neighbor, t_neighbor])
                            node_stack.append(valid_hop)
        else:
            return []
    return network_map


def _node_match(query_net: nx.MultiGraph, target_net: nx.MultiGraph, query_node: int, target_node: int) -> bool:
    """Special purpose matcher that ignores bond types, considering only if sites are bound. Internal states are
    matched normally."""
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
    """
Special purpose matcher that only compares bond types. Returns a tuple, where the first value is a boolean
holding whether the whole thing matched.

Rigidity in bonds in addition to site ordering!
Since there is at maximum one of any bond type per node in the network, finding it means finding the only path
like it, reducing the search space. This relies on the bonds being oriented, in this case I chose "outgoing" from
the current node. Since agent identifiers can be written in arbitrary order, I can't rely on just a<b comparison
at the identifier level to know if the bond's string was written in that same direction; to resolve this one must
compare the order of node introduction, which tracks the order of edge / node declaration.
    """
    match: bool = False
    # orient bonds so as to be read outgoing
    query_edges: List[Tuple[int, int, Dict]] = query_net.edges(query_node, data=True)
    query_bond_types: List[KappaBond] = []
    for here, dest, bond in query_edges:
        if here < dest:
            query_bond_types.append(bond['bond type'])
        else:
            query_bond_types.append(bond['bond type'].reverse())
    target_edges: List[Tuple[int, int, Dict]] = target_net.edges(target_node, data=True)
    target_bond_types: List[KappaBond] = []
    for here, dest, bond in target_edges:
        if here < dest:
            target_bond_types.append(bond['bond type'])
        else:
            target_bond_types.append(bond['bond type'].reverse())
    # check now-oriented bonds
    for query_bond_type in query_bond_types:
        if not any([query_bond_type == target_bond_type for target_bond_type in target_bond_types]):
            return match
    match = True
    return match

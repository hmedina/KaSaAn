#!/usr/bin/env python3
"""Contains `KappaComplex`, a class to represents a list of agents chained into a larger entity, and the `embed_and_map`
function."""

import xml.etree.ElementTree as ET
import re
import networkx as nx
from pathlib import Path
from collections import deque
from typing import Deque, Dict, List, Optional, Set, Tuple, Union

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
        if not isinstance(query, KappaAgent):
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
        if not isinstance(query, KappaComplex):
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
        if isinstance(query, KappaAgent):
            return self.get_number_of_embeddings_of_agent(query)
        elif isinstance(query, KappaComplex):
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
                    paired_bond_list.append(
                        (
                            dangle_bond_dict[bond]['agent id'],
                            agent_global_id,
                            int(bond),
                            {
                                'bond id': bond,
                                'bond type': this_bond_type,
                                'agent one id': dangle_bond_dict[bond]['agent id'],
                                'agent two id': agent_global_id
                                }))
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

    def to_graphml(self, outfile: Union[Path, str, None] = None, node_coloring: Optional[Dict[KappaAgent, any]] = None) -> ET.ElementTree:
        """Returns an XML ElementTree with a GraphML representation of the complex, using GraphML's ports for
         binding sites. If an output file is given, object is indented & serialized to that file.
         Optional argument `node_coloring` colorizes by single-agent patterns."""
        this_tree = self._kappa_to_graphml(node_coloring)
        if outfile is not None:
            ET.indent(this_tree, space='\t')
            if isinstance(outfile, str):
                this_tree.write(outfile, encoding='UTF-8', xml_declaration=True, method='xml')
            elif isinstance(outfile, Path):
                with outfile.open('wb') as f:
                    this_tree.write(file_or_filename=f, encoding='UTF-8', xml_declaration=True, method='xml')
        return this_tree


class NetMap():
    """
Class for representing network maps. The class does not store the networks it maps, only the indexes for edges and 
nodes. For a simple view, it can be printed as a string. For advanced & verbose view with network information, see 
`NetMap.pretty_format()`.
>>> from KaSaAn.core.KappaComplex import _traverse_from, KappaComplex, NetMap
>>> pattern_cyc_a = KappaComplex('x0:Axin(DIX-head[1], DIX-tail[20]), x1:Dvl(DIX-head[20], DIX-tail[1])').to_networkx()
>>> pattern_cyc_b = KappaComplex('x99:Dvl(DIX-head[100], DIX-tail[2]), x100:Axin(DIX-head[2], DIX-tail[100])').to_networkx()
>>> some_map: NetMap = _traverse_from(pattern_cyc_a, pattern_cyc_b, 0, 100)
>>> print(some_map)
Nodes: 1 -> 99, 0 -> 100
Edges: 1 -> 2, 20 -> 100
>>> print(some_map.pretty_format(pattern_cyc_a, pattern_cyc_b))
## Node mapping
┌─  x1:Dvl(DIX-head[20]{#} DIX-tail[1]{#})
└> x99:Dvl(DIX-head[100]{#} DIX-tail[2]{#})
┌─   x0:Axin(DIX-head[1]{#} DIX-tail[20]{#})
└> x100:Axin(DIX-head[2]{#} DIX-tail[100]{#})
## Edge mapping
┌─   x0:Axin(DIX-head[1])  <──>  x1:Dvl(DIX-tail[1])
└> x100:Axin(DIX-head[2])  <─>  x99:Dvl(DIX-tail[2])
┌─   x0:Axin(DIX-tail[ 20])  <──>  x1:Dvl(DIX-head[ 20])
└> x100:Axin(DIX-tail[100])  <─>  x99:Dvl(DIX-head[100])
    """

    def __init__(self):
        self.mapped_nodes_query: Set[int] = set()
        """Set of integers, holding the indexes of the nodes from the query pattern that have been matched (i.e. all)."""
        self.mapped_nodes_target: Set[int] = set()
        """Set of integers, holding the indexes of the nodes from the target object that have been matched."""
        self.node_map: Set[Tuple[int, int]] = set()
        """Set of tuples, holding the node indexes that matched from query to target networks."""
        self.edge_map: Set[Tuple[int, int]] = set()
        """Set of tuples, holding the edge indexes that matched from query to target networks."""

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
    
    def _can_node_map(self, query_ix: int, target_ix: int) -> bool:
        """
        Try to map the query's index to the target's index. Nodes can not be mapped to more than one image, but with 
        parallel edges in linear co-polymers, a cyclic dimer can edge-match and node-match. This method guards against 
        that by enforcing the check that no agents can map to more than one other.
        """
        if query_ix in self.mapped_nodes_query or target_ix in self.mapped_nodes_target:
            return False
        else:
            self.mapped_nodes_query.add(query_ix)
            self.mapped_nodes_target.add(target_ix)
            self.node_map.add((query_ix, target_ix))
            return True
    
    def _adjacency_check(self, query_net: nx.MultiGraph, target_net: nx.MultiGraph) -> bool:
        """
        For every edge, ergo pair of node indexes, that map from the query to the target graphs, verify the node maps
        correctly. This allows distinguishing cyclic dimers from linear polymeric species, which can't be done at the
        local level of bonds types.
        """
        # parallel edge guard: don't satisfy a linear trimer into a cyclic dimer
        if len(self.node_map) != query_net.number_of_nodes():
            return False
        if len(self.edge_map) != query_net.number_of_edges():
            return False
        # with size sorted, let's try to validate every bond type
        node_mapping = {}
        for (q_edge_ix, t_edge_ix) in self.edge_map:
            # since we can't just "get edge 98" without specifying origin and destination (networkX's edge keys are not unique
            # nor serve as identifiers <sigh>), we iterate and match the data block
            for item in query_net.edges(data='bond id'):
                if item[2]==str(q_edge_ix):
                    q_origin = item[0]
                    q_destin = item[1]
                    q_bond_type = query_net.adj[q_origin][q_destin][q_edge_ix]['bond type']
                    break
            for item in target_net.edges(data='bond id'):
                if item[2]==str(t_edge_ix):
                    t_origin = item[0]
                    t_destin = item[1]
                    t_bond_type = target_net.adj[t_origin][t_destin][t_edge_ix]['bond type']
                    break
            if q_bond_type == t_bond_type:
                pass
                # print('Mapping edge {} -> {} means nodes {} -> {} and {} -> {}'.format(q_edge_ix, t_edge_ix, q_origin, t_origin, q_destin, t_destin))
            elif q_bond_type == t_bond_type.reverse():
                swap = t_origin
                t_origin = t_destin
                t_destin = swap
                # print('Mapping edge {} -> {} means nodes {} -> {} and {} -> {} (corrected)'.format(q_edge_ix, t_edge_ix, q_origin, t_origin, q_destin, t_destin))
            # break if a node has already been mapped to something else; can't have one node mapped to two
            if q_origin in node_mapping:
                if node_mapping[q_origin] != t_origin:
                    return False
            else:
                node_mapping[q_origin] = t_origin
            if q_destin in node_mapping:
                if node_mapping[q_destin] != t_destin:
                    return False
            else:
                node_mapping[q_destin] = t_destin
        return True
    
    def pretty_format(self, query_net: nx.MultiGraph, target_net: nx.MultiGraph) -> str:
        """
        Format prettily the map with network data.
        >>> from KaSaAn.core.KappaComplex import _traverse_from, KappaComplex
        >>> pattern_cyc_a = KappaComplex('x0:Axin(DIX-head[1], DIX-tail[20]), x1:Dvl(DIX-head[20], DIX-tail[1])').to_networkx()
        >>> pattern_cyc_b = KappaComplex('x99:Dvl(DIX-head[100], DIX-tail[2]), x100:Axin(DIX-head[2], DIX-tail[100])').to_networkx()
        >>> some_map = _traverse_from(pattern_cyc_a, pattern_cyc_b, 0, 100)
        >>> print(some_map.pretty_format(pattern_cyc_a, pattern_cyc_b))
        ## Node mapping
        ┌─  x1:Dvl(DIX-head[20]{#} DIX-tail[1]{#})
        └> x99:Dvl(DIX-head[100]{#} DIX-tail[2]{#})
        ┌─   x0:Axin(DIX-head[1]{#} DIX-tail[20]{#})
        └> x100:Axin(DIX-head[2]{#} DIX-tail[100]{#})
        ## Edge mapping
        ┌─   x0:Axin(DIX-head[1])  <──>  x1:Dvl(DIX-tail[1])
        └> x100:Axin(DIX-head[2])  <─>  x99:Dvl(DIX-tail[2])
        ┌─   x0:Axin(DIX-tail[ 20])  <──>  x1:Dvl(DIX-head[ 20])
        └> x100:Axin(DIX-tail[100])  <─>  x99:Dvl(DIX-head[100])
        """
        # generate node mapping string list
        output_string_list = ['## Node mapping']
        for node_q, node_t in self.node_map:
            ka_agent_q = query_net.nodes[node_q]['kappa']
            ka_agent_t = target_net.nodes[node_t]['kappa']
            ag1_pad = ' ' * len(str(node_t))    # attention: one agent's index size
            ag2_pad = ' ' * len(str(node_q))    # informs >the other's< padding
            l_1 = '┌─' + ag1_pad + '{ka}'.format(ka=ka_agent_q)
            l_2 = '└>' + ag2_pad + '{ka}'.format(ka=ka_agent_t)
            output_string_list.append(l_1 + '\n' + l_2)
        # generate edge mapping string list
        output_string_list.append('## Edge mapping')
        for edge_q, edge_t in self.edge_map:
            for item in query_net.edges(data='bond id'):
                if item[2]==str(edge_q):
                    q_origin = item[0]
                    q_destin = item[1]
                    q_bond_type:KappaBond = query_net.adj[q_origin][q_destin][edge_q]['bond type']
                    break
            for item in target_net.edges(data='bond id'):
                if item[2]==str(edge_t):
                    t_origin = item[0]
                    t_destin = item[1]
                    t_bond_type:KappaBond = target_net.adj[t_origin][t_destin][edge_t]['bond type']
                    break
            if q_bond_type == t_bond_type.reverse():
                swap = t_origin
                t_origin = t_destin
                t_destin = swap
                t_bond_type = t_bond_type.reverse()
            l_a_ag1_pad = ' ' * len(str(t_origin))
            l_b_ag1_pad = ' ' * len(str(q_origin))
            l_a_ag2_pad = '─' * len(str(t_destin))
            l_b_ag2_pad = '─' * len(str(q_destin))
            edge_pad = len(str(max(edge_q, edge_t)))
            l_a_agent_1 = 'x{q_origin}:{origin_agent}({origin_site}[{i:{width}}])'.format(q_origin=q_origin, origin_agent=q_bond_type.agent_one, origin_site=q_bond_type.site_one, i=edge_q, width=edge_pad)
            l_a_agent_2 = 'x{q_destin}:{destin_agent}({destin_site}[{i:{width}}])'.format(q_destin=q_destin, destin_agent=q_bond_type.agent_two, destin_site=q_bond_type.site_two, i=edge_q, width=edge_pad)
            l_b_agent_1 = 'x{t_origin}:{origin_agent}({origin_site}[{i:{width}}])'.format(t_origin=t_origin, origin_agent=t_bond_type.agent_one, origin_site=t_bond_type.site_one, i=edge_t, width=edge_pad)
            l_b_agent_2 = 'x{t_destin}:{destin_agent}({destin_site}[{i:{width}}])'.format(t_destin=t_destin, destin_agent=t_bond_type.agent_two, destin_site=t_bond_type.site_two, i=edge_t, width=edge_pad)
            line_a = '┌─' + l_a_ag1_pad + l_a_agent_1 + '  <' + l_a_ag2_pad + '>  ' + l_a_agent_2
            line_b = '└>' + l_b_ag1_pad + l_b_agent_1 + '  <' + l_b_ag2_pad + '>  ' + l_b_agent_2
            output_string_list.append(line_a + '\n' + line_b)
        return '\n'.join(output_string_list)



def embed_and_map(ka_query: KappaComplex, ka_target: KappaComplex) -> Tuple[List[NetMap], Set[NetMap]]:
    """
Calculates all the embeddings of `ka_query` into `ka_target`. First element is the list of all mappings,
while second is the set of automorphism-corrected mappings. For a rotational symmetry:
>>> from KaSaAn.core.KappaComplex import embed_and_map, KappaComplex
>>> my_comp = KappaComplex('Bob(h[10], t[11]), Bob(h[11], t[12]), Bob(h[12], t[10])')
>>> maps_all, maps_unique = embed_and_map(my_comp, my_comp)
>>> print(maps_all[0])
Nodes: 1 -> 1, 2 -> 2, 0 -> 0
Edges: 10 -> 10, 12 -> 12, 11 -> 11
>>> print(maps_all[1])
Nodes: 0 -> 1, 1 -> 2, 2 -> 0
Edges: 11 -> 12, 12 -> 10, 10 -> 11
>>> print(maps_all[2])
Nodes: 1 -> 0, 0 -> 2, 2 -> 1
Edges: 12 -> 11, 10 -> 12, 11 -> 10
>>> print(maps_unique)
Nodes: 1 -> 1, 2 -> 2, 0 -> 0
Edges: 10 -> 10, 12 -> 12, 11 -> 11

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


def _traverse_from(query_net: nx.MultiGraph, target_net: nx.MultiGraph, q_start: int, t_start: int) -> Optional[NetMap]:
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
        node_matched: bool = _node_match(query_net, target_net, q_node, t_node)
        edge_matched: bool = _edge_match(query_net, target_net, q_node, t_node)
        if node_matched and edge_matched:
            # prepare for next iteration:
            #  guard against agents being double-mapped in co-polymer & rings scenario, then
            #  add nodes of query, mapped to their images in target, to the node map;
            #  add neighbors of query, mapped to their images in target;
            #  add their respective bonds, mapped to their images in target, to the edge map
            valid_node_map = network_map._can_node_map(q_node, t_node)
            if valid_node_map:
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
            return None
    if network_map._adjacency_check(query_net, target_net):
        return network_map
    else:
        return None


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

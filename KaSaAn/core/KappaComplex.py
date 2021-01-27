#!/usr/bin/env python3

import re
import networkx as nx
from typing import List, Set, Dict

from .KappaEntity import KappaEntity
from .KappaAgent import KappaAgent
from .KappaError import ComplexParseError, AgentParseError


class KappaComplex(KappaEntity):
    """Class for representing Kappa complexes. I.e. 'A(b[1] s{u}[.]), B(a[1] c[2]), C(b[2] a[3]), A(c[3] s[.]{x})'.
    Note these must be connected components."""

    def __init__(self, expression: str):
        self._raw_expression: str
        self._agents: List[KappaAgent]
        self._agent_identifiers: List[int]
        self._agent_types: Set[KappaAgent]
        self._kappa_expression: str
        self._composition: Dict[KappaAgent, int]

        self._raw_expression = expression
        # get the set of agents making up this complex
        agent_idnt_pat = r'(?:x\d+:)?'
        agent_name_pat = r'(?:[_~][a-zA-Z0-9_~+-]+|[a-zA-Z][a-zA-Z0-9_~+-]*)'
        agent_sign_pat = r'\([^()]*\)'
        matches = re.findall(agent_idnt_pat + agent_name_pat + agent_sign_pat, expression.strip())
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
        self._composition = composition
        # canonicalize the kappa expression
        self._kappa_expression = ', '.join([str(agent) for agent in self._agents])

    def get_number_of_bonds(self) -> int:
        """Returns the number of bonds in the complex."""
        bonds = set()
        for agent in self._agents:
            bonds.update(agent.get_bond_identifiers())
        return len(bonds)

    def get_size_of_complex(self) -> int:
        """Returns the size, in agents, of this complex. This works by counting the number of agent signatures with
        their open/close parentheses."""
        return len(self._agents)

    def get_agent_types(self) -> Set[KappaAgent]:
        """Returns the set of agent names that make up the complex."""
        return self._agent_types

    def get_all_agents(self) -> List[KappaAgent]:
        """Returns a list of KappaAgents, filled with agents plus their signatures, present in this complex."""
        # replace commas with spaces, then split string into a list at closing parenthesis
        return self._agents

    def get_number_of_embeddings_of_agent(self, query) -> int:
        """Returns the number of embeddings the query agent has on the KappaComplex. Does not follow bonds,
        so effectively the query must be a single-agent."""
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

    def get_complex_composition(self) -> Dict[KappaAgent, int]:
        """Returns a dictionary where the key is an agent, and the value the number of times that agent appears in
        this complex."""
        return self._composition

    def get_number_of_embeddings_of_complex(self, query: str) -> int:
        """Returns the number of embedding the query complex has on the KappaComplex. Follows bonds. WIP"""
        raise NotImplementedError

    def get_agent_identifiers(self) -> List[int]:
        """Returns a list with the numeric agent identifiers, if any."""
        return self._agent_identifiers

    def to_networkx(self, identifier_offset: int = 0) -> nx.MultiGraph:
        """Returns a Multigraph representation of the complex, abstracting away binding site data. Nodes represent
        agents, edges their bonds. Nodes have an attribute dictionary where the key 'kappa' holds the KappaAgent.
        Edges have an attribute dictionary where the key 'bond id' holds the bond identifier from the Kappa expression.
        Node identifiers are integers, using the order of agent declaration. For a graph g, g.nodes.data() displays the
        node identifiers and their corresponding KappaAgents, and g.edges.data() displays the edges, using the node
        identifiers as well as the kappa identifiers. The optional parameter 'identifier_offset' will offset all
        numeric identifiers reported; used in unlabeled snapshots, or when combining graphs."""
        kappa_complex_multigraph = nx.MultiGraph()
        dangle_bond_list = {}                       # store unpaired bonds here
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
                if bond in dangle_bond_list:
                    paired_bond_list.append((dangle_bond_list[bond], agent_global_id, {'bond id': bond}))
                    del dangle_bond_list[bond]
                else:
                    dangle_bond_list[bond] = agent_global_id
            agent_counter += 1
        if dangle_bond_list:
            raise ValueError('Dangling bonds <' + ','.join(dangle_bond_list.keys()) +
                             '> found in complex: ' + self._raw_expression)
        kappa_complex_multigraph.add_edges_from(paired_bond_list)
        return kappa_complex_multigraph

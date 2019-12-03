#!/usr/bin/env python3

import re
from typing import List, Set, Dict

from .KappaEntity import KappaEntity
from .KappaAgent import KappaAgent
from .KappaError import ComplexParseError, AgentParseError


class KappaComplex(KappaEntity):
    """Class for representing Kappa complexes. I.e. 'A(b[1] s{u}[.]), B(a[1] c[2]), C(b[2] a[3]), A(c[3] s[.]{x})'.
    Notice these must be connected components."""

    def __init__(self, expression: str):
        self._raw_expression: str
        self._agents: List[KappaAgent]
        self._agent_types: Set[KappaAgent]
        self._kappa_expression: str

        self._raw_expression = expression
        # get the set of agents making up this complex
        agent_name_pat = r'(?:[_~][a-zA-Z0-9_~+-]+|[a-zA-Z][a-zA-Z0-9_~+-]*)'
        agent_sign_pat = r'\([^()]*\)'
        matches = re.findall(agent_name_pat + agent_sign_pat, expression.strip())
        if len(matches) == 0:
            raise ComplexParseError('Complex <' + self._raw_expression + '> appears to have zero agents.')
        try:
            self._agents = sorted([KappaAgent(item) for item in matches])
        except AgentParseError as a:
            raise ComplexParseError('Could not parse agents in complex <' + expression + '>.') from a
        self._agent_types = set([KappaAgent(agent.get_agent_name() + '()') for agent in self._agents])
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
        composition = {}
        for agent in self._agent_types:
            composition[agent] = self.get_number_of_embeddings_of_agent(agent)
        return composition

    def get_number_of_embeddings_of_complex(self, query: str) -> int:
        """Returns the number of embedding the query complex has on the KappaComplex. Follows bonds. WIP"""
        raise NotImplementedError

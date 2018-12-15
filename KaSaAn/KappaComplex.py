#! /usr/bin/python3

import re
from typing import List, Set, Dict
from .KappaAgent import KappaAgent
from .KappaError import ComplexParseError, AgentParseError


class KappaComplex:
    """Class for representing Kappa complexes. I.e. 'A(b[1] s{u}[.]), B(a[1] c[2]), C(b[2] a[3]), A(c[3] s[.]{x})'.
    Notice these must be connected components."""

    def __init__(self, expression: str):
        self.raw_expression: str
        self.agents: List[KappaAgent]
        self.agent_types: Set[KappaAgent]
        self.kappa_expression: str

        self.raw_expression = expression
        # get the set of agents making up this complex
        matches = re.findall('([a-zA-Z][\w\-_]*\([^()]*\))', expression.strip())
        if len(matches) == 0:
            raise ComplexParseError('Complex <' + self.raw_expression + '> appears to have zero agents.')
        try:
            self.agents = [KappaAgent(item) for item in matches]
        except AgentParseError as a:
            raise ComplexParseError('Could not parse agents in complex <' + expression + '>.') from a
        self.agent_types = set([KappaAgent(agent.agent_name + '()') for agent in self.agents])
        # canonicalize the kappa expression
        self.kappa_expression = ', '.join([str(agent) for agent in self.agents])

    def __repr__(self) -> str:
        return 'KappaComplex("{0}")'.format(self.kappa_expression)

    def __str__(self) -> str:
        return self.kappa_expression

    def get_number_of_bonds(self) -> int:
        """Returns the number of bonds in the complex."""
        matches = re.findall('\[\d+\]', self.kappa_expression)
        if not len(matches) % 2 == 0:
            raise ValueError('Number of bond termini not an even number in <' + self.kappa_expression + '>')
        return int(len(matches) / 2)

    def get_size_of_complex(self) -> int:
        """Returns the size, in agents, of this complex. This works by counting the number of agent signatures with
        their open/close parentheses."""
        matches = re.findall('\([^)]*\)', self.kappa_expression)
        return int(len(matches))

    def get_agent_types(self) -> Set[KappaAgent]:
        """Returns the set of agent names that make up the complex."""
        return self.agent_types

    def get_agents(self) -> List[KappaAgent]:
        """Returns a list of KappaAgents, filled with agents plus their signatures, present in this complex."""
        # replace commas with spaces, then split string into a list at closing parenthesis
        return self.agents

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
        for s_agent in self.agents:
            if q_agent in s_agent:
                match_number += 1
        return match_number

    def get_complex_composition(self) -> Dict[KappaAgent, int]:
        """Returns a dictionary where the key is an agent, and the value the number of times that agent appears in
        this complex."""
        composition = {}
        for agent in self.agent_types:
            composition[agent] = self.get_number_of_embeddings_of_agent(agent)
        return composition

    def get_number_of_embeddings_of_complex(self, query: str) -> int:
        """Returns the number of embedding the query complex has on the KappaComplex. Follows bonds. WIP"""
        raise NotImplemented


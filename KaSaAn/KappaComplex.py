#! /usr/bin/python3

import re
from .KappaAgent import KappaAgent


class KappaComplex:
    """Class for representing Kappa complexes. I.e. 'A(b[1] s{u}), B(a[1] c[2]), C(b[2] a[3]), A(c[3] s{x})'. Notice
     these must be connected components."""

    def __init__(self, kappa_expression):
        """The constructor also removes spaces from the expression."""
        self.kappa_expression = kappa_expression

    def get_number_of_bonds(self):
        """Returns the number of bonds in the complex."""
        matches = re.findall('\[\d+\]', self.kappa_expression)
        return int(len(matches) / 2)

    def get_size_of_complex(self):
        """Returns the size, in agents, of this complex. This works by counting the number of agent signatures with
        their open/close parentheses."""
        matches = re.findall('\([^)]*\)', self.kappa_expression)
        return int(len(matches))

    def get_agent_types(self):
        """Returns the set of agents that make up the complex. This works by counting the number of non-digit-leading
        words that have a set of open/close parenthesis directly after them."""
        matches = re.findall('([a-zA-Z][\w\-_]*)\([^)]*\)', self.kappa_expression)
        agents = set(matches)
        return agents

    def get_agents(self):
        """Returns a list of KappaAgents, filled with agents plus their signatures, present in this complex."""
        agent_list = self.kappa_expression.split(', ')
        agent_list = [KappaAgent(item) for item in agent_list]
        return agent_list

    def get_number_of_embeddings_of_agent(self, query):
        """Returns the number of embeddings the query agent has on the KappaComplex. Does not follow bonds,
        so effectively the query must be a single-agent."""
        kappa_query = KappaComplex(query)
        match_number = 0
        # Internally, this uses two tokens: match_number returns the number of embeddings the query has on this agent,
        # whereas match_score is used to track all the sites within a query have been matched.
        # First, we iterate over the agents in our complex
        for s_agent in self.get_agents():
            # Secondly, we iterate over the agents in the query
            for q_agent in kappa_query.get_agents():
                # If agent names match, we move to evaluate sites
                if s_agent.agent_name == q_agent.agent_name:
                    match_score = 0
                    # Thirdly, we iterate over the query's sites
                    for q_site in q_agent.agent_signature:
                        if s_agent.contains_site_with_states(q_site):
                            match_score += 1
                    # This counter keeps track of how many fully-matched queries we've embedded
                    if match_score == len(q_agent.agent_signature):
                        match_number += 1
        return match_number

    def get_complex_composition(self):
        """Returns a dictionary where the key is an agent name, and the value the number of times that agent appears in
        this complex."""
        composition = {}
        for agent in self.get_agent_types():
            composition[agent] = self.get_number_of_embeddings_of_agent(agent + '()')
        return composition

    def get_number_of_embeddings_of_complex(self, query):
        """Returns the number of embedding the query complex has on the KappaComplex. Follows bonds. WIP"""
        raise NotImplemented


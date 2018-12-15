#! /usr/bin/python3

import re
from typing import List
from .KappaSite import KappaSite
from .KappaError import AgentParseError, SiteParseError


class KappaAgent:
    """Class for representing Kappa agents. I.e. <<A(b[1])>> or <<A(s{a}[.] a[1] b[.])>>."""

    def __init__(self, expression: str):
        self.raw_expression: str
        self.agent_name: str
        self.agent_signature: List[KappaSite]
        self.kappa_expression: str

        # Check if kappa expression's name & overall structure is valid
        matches = re.match('^([a-zA-Z][\w\-_]*)\(([^()]*)\)$', expression.strip())
        if not matches:
            matches = re.match('^([a-zA-Z][\w\-_]*)\(([^()]*)\)$', expression.strip() + '()')
        if not matches:
            raise AgentParseError('Invalid agent declaration <' + expression + '>')
        self.raw_expression = expression

        # assign stuff to variables
        self.agent_name = matches.group(1)
        ag_signature = matches.group(2)
        if ag_signature == '':
            site_list = []
        else:
            # Kappa4 allows commas or whitespace as separators:
            # swap all commas for spaces, then split by whitespace, then sort alphabetically
            site_list = sorted(ag_signature.replace(',', ' ').split())
        self.agent_signature = [KappaSite(site) for site in site_list]
        # canonicalize the kappa expression
        self.kappa_expression = self.agent_name + '(' + ' '.join([str(site) for site in self.agent_signature]) + ')'

    def __repr__(self) -> str:
        return 'KappaAgent("{0}")'.format(self.kappa_expression)

    def __str__(self) -> str:
        return self.kappa_expression

    def __eq__(self, other) -> bool:
        # make it a KappaAgent if it's not one already
        if not type(other) is KappaAgent:
            other = KappaAgent(other)
        # as the kappa expression has been canonicalized, equality testing is straightforward
        if self.kappa_expression == other.kappa_expression:
            return True
        else:
            return False

    def __hash__(self) -> int:
        return hash(self.kappa_expression)

    def __contains__(self, item) -> bool:
        # type parsing: try to make it an Agent, if that fails try a Site, if that tails, raise exception
        if (not type(item) is KappaSite) and (not type(item) is KappaAgent):
            try:
                try:
                    item = KappaAgent(item)
                except AgentParseError:
                    item = KappaSite(item)
            except SiteParseError:
                raise ValueError('Could not parse <' + item + '> as an Agent nor as a Site')
        # once item has been typed, or if it was properly typed, then we can decide what comparison to do
        if type(item) is KappaSite:
            for site in self.agent_signature:
                if item in site:
                    return True
        elif type(item) is KappaAgent:
            if item.agent_name ==  self.agent_name:
                counter  = 0
                for site in item.agent_signature:
                    if site in self:
                        counter += 1
                if counter == len(item.agent_signature):
                    return True

    def get_agent_name(self) -> str:
        """Return a string with the agent's name."""
        return self.agent_name

    def get_agent_signature(self) -> List[KappaSite]:
        """Return a list of strings with the agent's signature."""
        return self.agent_signature

    def get_bond_identifiers(self) -> List[str]:
        """Return the list of bonds ending/starting at this agent, e.g. for <<A(a[.] b[1] c[2] d{a}[.])>> these would
         be the list ['1','2']."""
        agent_bonds = []
        for item in self.agent_signature:
            g = re.match('(\d+)', item.bond_state)
            if g:
                agent_bonds.append(g.group(1))
        return agent_bonds

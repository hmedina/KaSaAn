#! /usr/bin/python3

import re
from typing import List
from .KappaEntity import KappaEntity
from .KappaSite import KappaPort, KappaCounter, KappaSite
from .KappaError import AgentParseError, PortParseError, CounterParseError


class KappaAgent(KappaEntity):
    """Class for representing Kappa agents. I.e. <<A(b[1])>> or <<A(s{a}[.] a[1] b[.])>>."""

    def __init__(self, expression: str):
        self._raw_expression: str
        self._agent_name: str
        self._agent_signature: List[KappaSite]
        self._kappa_expression: str

        # Check if kappa expression's name & overall structure is valid
        agent_name_pat = '([_~][a-zA-Z0-9_~+-]+|[a-zA-Z][a-zA-Z0-9_~+-]*)'
        agent_sign_pat = '\(([^()]*)\)'
        agent_pat = '^' + agent_name_pat + agent_sign_pat + '$'
        matches = re.match(agent_pat, expression.strip())
        if not matches:
            matches = re.match(agent_pat, expression.strip() + '()')
        if not matches:
            raise AgentParseError('Invalid agent declaration <' + expression + '>')
        self._raw_expression = expression

        # assign to variables
        self._agent_name = matches.group(1)
        ag_signature = matches.group(2)
        if ag_signature == '':
            site_list = []
        else:
            # Kappa4 allows commas or whitespace as separators:
            # swap all commas for spaces, then split by whitespace, then sort alphabetically
            site_list = sorted(ag_signature.replace(',', ' ').split())
        self._agent_signature = []
        for entry in site_list:
            try:
                try:
                    site = KappaPort(entry)
                except PortParseError:
                    site = KappaCounter(entry)
            except CounterParseError:
                raise ValueError('Could not parse <' + entry + '> as a Port nor as a Counter')
            self._agent_signature.append(site)

        # canonicalize the kappa expression
        self._kappa_expression = self._agent_name + '(' + ' '.join([str(site) for site in self._agent_signature]) + ')'

    def __contains__(self, item) -> bool:
        # type parsing: try to make it an Agent, if that fails try a Site, if that tails, raise exception
        if (not type(item) is KappaPort) and (not type(item) is KappaCounter) and (not type(item) is KappaAgent):
            try:
                try:
                    try:
                        item = KappaAgent(item)
                    except AgentParseError:
                        item = KappaPort(item)
                except PortParseError:
                    item = KappaCounter(item)
            except CounterParseError:
                raise ValueError('Could not parse <' + item + '> as an Agent, nor as a Port, nor a Counter')
        # once item has been typed, or if it was properly typed, then we can decide what comparison to do
        if type(item) is KappaPort:
            for site in self._agent_signature:
                if item in site:
                    return True
        elif type(item) is KappaCounter:
            for site in self._agent_signature:
                if item == site:
                    return True
        elif type(item) is KappaAgent:
            if item._agent_name ==  self._agent_name:
                counter  = 0
                for site in item._agent_signature:
                    if site in self:
                        counter += 1
                if counter == len(item._agent_signature):
                    return True

    def get_agent_name(self) -> str:
        """Return a string with the agent's name."""
        return self._agent_name

    def get_agent_signature(self) -> List[KappaSite]:
        """Return a list of strings with the agent's signature."""
        return self._agent_signature

    def get_bond_identifiers(self) -> List[str]:
        """Return the list of bonds ending/starting at this agent, e.g. for <<A(a[.] b[1] c[2] d{a}[.])>> these would
         be the list ['1','2']."""
        agent_bonds = []
        for item in self._agent_signature:
            if type(item) is KappaPort:
                agent_bonds.append(item.get_port_bond_state())
        agent_bonds = [b for b in agent_bonds if b != '.' and b != '_' and b != '#']
        return agent_bonds

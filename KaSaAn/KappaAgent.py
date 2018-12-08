#! /usr/bin/python3

import re
from typing import List


def site_contains_site(host: str, query: str) -> bool:
    """Helper function for the KappaAgent class. It deconstructs a query and a target into three components: name,
    internal state, and bond state. It then compares these three to determine if target contains query. For the query,
    this function supports Kappa4 wildcards: <<#>> for <<whatever state>>, <<_>> for <<bound to whatever>>."""

    # Breakout the structure of the site: name{internal}[bond]{internal}
    h_matches = re.match('^([a-zA-Z][\w\-_]*)({\w+})?(\[\d+\]|\[\.\])?({\w+})?', host)
    h_site_name = h_matches.group(1) if h_matches.group(1) else None
    h_site_bond = h_matches.group(3)[1:-1] if h_matches.group(3) else None
    # Since internal and binding states can be stated in any order, I accommodate the ambiguity by first trying to match
    # against group 2, then against group 4
    if h_matches.group(2):
        h_site_state = h_matches.group(2)[1:-1]
    elif h_matches.group(4):
        h_site_state = h_matches.group(4)[1:-1]
    else:
        h_site_state = None

    # Breakout the structure of the site (can have wildcards): name{internal}[bond]{internal}
    q_matches = re.match('^([a-zA-Z][\w\-_]*)({\w+}|{#})?(\[\d+\]|\[\.\]|\[_\]|\[#\])?({\w+}|{#})?', query)
    q_site_name = q_matches.group(1) if q_matches.group(1) else None
    q_site_bond = q_matches.group(3)[1:-1] if q_matches.group(3) else None
    # Since internal and binding states can be stated in any order, I accommodate the ambiguity by first trying to match
    # against group 2, then against group 4
    if q_matches.group(2):
        q_site_state = q_matches.group(2)[1:-1]
    elif q_matches.group(4):
        q_site_state = q_matches.group(4)[1:-1]
    else:
        q_site_state = None

    #print('H: ' + h_site_name + ' | ' + h_site_state + ' | ' + h_site_bond)
    #print('Q: ' + q_site_name + ' | ' + q_site_state + ' | ' + q_site_bond)

    # Begin matching query against host
    sites_match = False
    if q_site_name == h_site_name:
        # Check if internal states match
        if q_site_state == '#' or q_site_state == h_site_state:
            # Check if bond states match
            if q_site_bond == '#':
                sites_match = True
            elif q_site_bond == '_' and h_site_bond != '.':
                sites_match = True
            elif q_site_bond == h_site_bond:
                sites_match = True

    return sites_match


class KappaAgent:
    """Class for representing Kappa agents. I.e. <<A(b[1])>> or <<A(s{a}[.] a[1] b[.])>>."""
    kappa_expression: str
    agent_name: str
    agent_signature: List[str]


    def __init__(self, expression: str):
        # Check if kappa expression's name & overall structure is valid
        matches = re.match('([a-zA-Z][\w\-_]*)\(([^)]*)\)', expression.strip())
        assert matches, 'Invalid kappa expression <<' + expression + '>>'

        # Assign results to variables
        self.kappa_expression = expression
        self.agent_name = matches.group(1)
        if matches.group(2) == '':
            self.agent_signature = []
        else:
            agent_signature = matches.group(2)
            # as Kappa4 allows commas or whitespace as separators, I first swap all commas for spaces, then split
            # by whitespace
            self.agent_signature = agent_signature.replace(',', ' ').split()

    def __repr__(self):
        return 'KappaAgent("{0}")'.format(self.kappa_expression)

    def __str__(self):
        return self.kappa_expression

    def contains_site_with_states(self, query_site: str) -> bool:
        """Return true or false, depending on whether the agent contains the query site and the specified states."""
        matches = False
        for s_site in self.agent_signature:
            if site_contains_site(s_site, query_site):
                matches = True
                break
        return matches

    def contains_site(self, query_site: str) -> bool:
        """Return true or false, depending on whether the agent contains the query site."""
        matches = False
        for s_site in self.agent_signature:
            if site_contains_site(s_site, query_site + '[#]{#}'):
                matches = True
                break
        return matches

    def get_bond_identifiers(self) -> list:
        """Return the list of bonds ending/starting at this agent, e.g. for <<A(a[.] b[1] c[2] d{a}[.])>> these would
         be the list ['1','2']."""
        agent_bonds = []
        for item in self.agent_signature:
            matches = re.match('[a-zA-Z]\w*({[^}]+})?\[(\d+)\]', item)
            if matches:
                agent_bonds.append(matches.group(2))
        return agent_bonds

#!/usr/bin/env python3
"""Contains the `KappaRule` class."""

import re
from typing import List, Set

from .KappaAgent import KappaAgent, KappaToken
from .KappaComplex import KappaComplex
from .KappaEntity import KappaEntity
from .KappaError import RuleParseError


class KappaRule(KappaEntity):
    """Class to represent a Kappa Rule. Work in Progress."""
    def __init__(self, raw_expression: str):
        self._name: str
        self._pattern: str
        self._rate_pri: str
        self._rate_uni: str
        self._horizon: int
        self._agent_expression: str
        self._token_expression: str
        self._agents: List[KappaAgent]
        self._tokens: List[KappaToken]
        self._kappa_expression: str

        # remove spaces, breaks, comments
        digested_rule = re.sub(r'\s+|\t+|\n+', ' ', raw_expression)  # Remove line breaks, tabs, multi-spaces
        digested_rule = re.sub(r'/\*[^*/]*\*/', '', digested_rule)   # Remove in-line comment
        digested_rule = digested_rule.split('//')[0]                # Remove trailing comment, leading/trialing spaces
        digested_rule = digested_rule.strip()
        if '->' in digested_rule:
            raise RuleParseError('Rule parsing only supports edit notation, not chemical notation.')

        # extract rule name, Kappa pattern, rates
        rule_components = re.match(r"('.+')?\s*(.+)\s*@\s*([^{]+)\s*(?:{([^}]+)})?", digested_rule)
        if not rule_components:
            raise ValueError('Could not parse pattern <' + digested_rule + '> as a rule')
        self._name = rule_components.group(1).strip() if rule_components.group(1) else ''
        self._pattern = rule_components.group(2).strip() if rule_components.group(2) else ''
        self._rate_pri = rule_components.group(3).strip() if rule_components.group(3) else ''
        self._rate_uni = rule_components.group(4).strip() if rule_components.group(4) else ''
        if self._rate_uni:
            if ':' in self._rate_uni:
                parts = self._rate_uni.split(':')
                self._rate_uni = parts[0].strip()
                self._horizon = int(parts[1].strip())
            else:
                self._horizon = None
        else:
            self._horizon = None
        if not self._pattern:
            raise RuleParseError('No rule expression found in <' + digested_rule + '>')
        if not self._rate_pri:
            raise RuleParseError('No primary rate found in <' + digested_rule + '>')

        # extract & process entities: agents & tokens
        agents_and_tokens = re.match(r'([^|]+)?\s*\|?\s*(.+)?', self._pattern)
        if not agents_and_tokens:
            raise RuleParseError('Could not find agents nor tokens in <' + self._pattern + '> expression')
        # process agents
        if agents_and_tokens.group(1):
            self._agent_expression = agents_and_tokens.group(1).strip()
            self._agents = KappaComplex(self._agent_expression).get_all_agents()
        else:
            self._agent_expression = ''
            self._agents = []
        # process tokens
        if agents_and_tokens.group(2):
            self._token_expression = agents_and_tokens.group(2).strip()
            self._tokens = [KappaToken(item) for item in self._token_expression.split(',')]
        else:
            self._token_expression = ''
            self._tokens = []

        # canonicalize the kappa expression
        c_name = self._name + ' ' if self._name else ''
        c_agnt = ', '.join([str(ag) for ag in self._agents])
        c_tokn = ' | ' + ', '.join([str(tk) for tk in self._tokens]) if self._tokens else ''
        c_rt_p = ' @ ' + self._rate_pri
        if self._rate_uni:
            if self._horizon:
                c_rt_u = ' { ' + self._rate_uni + ' : ' + str(self._horizon) + ' } '
            else:
                c_rt_u = ' { ' + self._rate_uni + ' } '
        else:
            c_rt_u = ''
        self._kappa_expression = (c_name + c_agnt + c_tokn + c_rt_p + c_rt_u).strip()

    def get_name(self) -> str:
        """Returns a string with the name of this rule."""
        return self._name

    def get_rate_primary(self) -> str:
        """Returns a string with the primary (usually binary) rate for this rule."""
        return self._rate_pri

    def get_rate_unary(self) -> str:
        """Returns a string with the unary rate for this rule, if specified."""
        return self._rate_uni

    def get_horizon(self) -> int:
        """Returns an integer with the molecular horizon for this rule's unary rate."""
        return self._horizon

    def get_agents(self) -> List[KappaAgent]:
        """Returns a list with the KappaAgents in this rule."""
        return self._agents

    def get_tokens(self) -> List[KappaToken]:
        """Returns a list with the KappaTokens in this rule."""
        return self._tokens

    def get_bond_identifiers(self) -> Set[str]:
        """Returns a set with the bond identifiers present in this rule."""
        idents = []
        for agent in self._agents:
            idents += agent.get_bond_identifiers()
        return set(idents)

#!/usr/bin/env python3

from .KappaEntity import KappaEntity


class KappaBond(KappaEntity):
    """Class for representing kappa typed bonds."""

    def __init__(self, agent_one: str, site_one: str, agent_two: str, site_two: str):
        self._kappa_expression: str

        # canonicalize expression
        if agent_one < agent_two:
            self._kappa_expression = agent_one + '.' + site_one + '..' + site_two + '.' + agent_two
        elif agent_two < agent_one:
            self._kappa_expression = agent_two + '.' + site_two + '..' + site_one + '.' + agent_one
        else:
            if site_one < site_two:
                self._kappa_expression = agent_one + '.' + site_one + '..' + site_two + '.' + agent_two
            else:
                self._kappa_expression = agent_two + '.' + site_two + '..' + site_one + '.' + agent_one

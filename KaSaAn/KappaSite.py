#! /usr/local/bin/python3
import re
from .KappaEntity import KappaEntity
from .KappaError import PortParseError, CounterParseError
from abc import abstractmethod


class KappaSite(KappaEntity):
    @abstractmethod
    def __init__(self):
        pass


class KappaPort(KappaSite):
    """Class for representing traditional Kappa Sites, e.g. 's[3]', 'g[.]{b}', or 'k[_]{#}'."""

    def __init__(self, expression: str):
        self._raw_expression: str
        self._port_name: str
        self._bond_state: str
        self._int_state: str
        self._kappa_expression: str

        self._raw_expression = expression

        # define patterns that make up a site
        port_name_pat = '([_~][a-zA-Z0-9_~+-]+|[a-zA-Z][a-zA-Z0-9_~+-]*)'
        int_state_pat = '(?:{(\w+|#|=\d+)})?'
        bnd_state_pat = '\[(.|_|#|\d+)\]'
        port_pat = '^' + port_name_pat + int_state_pat + bnd_state_pat + int_state_pat + '$'
        # parse assuming full site declaration, with bond state declared
        g = re.match(port_pat, expression.strip())
        # if that fails, try parsing with bond state explicitly declared as a wildcard
        if not g:
            g = re.match(port_pat, expression.strip() + '[#]')
        # if that fails, throw an error
        if not g:
            raise PortParseError('Invalid port declaration <' + expression + '>')
        # assuming it parsed, assign capturing groups to variables
        self._port_name = g.group(1)
        self._bond_state = g.group(3)
        # internal states, unless specified, will default to wildcard '#'
        if g.group(2):
            self._int_state = g.group(2)
        elif g.group(4):
            self._int_state = g.group(4)
        else:
            self._int_state = '#'
        # canonicalize the kappa expression
        self._kappa_expression = self._port_name + '[' + self._bond_state + ']{' + self._int_state + '}'

    def __contains__(self, item) -> bool:
        # we can't compare ports to counters
        if type(item) is KappaCounter:
            raise PortParseError('Can not check for containment of supplied counter <' + item +
                                 '> in port <' + self._kappa_expression + '>')
        # make it a KappaPort if it's not one already
        elif not type(item) is KappaPort:
            item = KappaPort(item)
        # check if item is in self, Kappa-wise
        contains = False
        if self._port_name == item._port_name:
            if item._int_state == '#':
                if item._bond_state == '#':
                    contains = True
                elif (item._bond_state == '_') & (self._bond_state != '.'):
                    contains = True
                elif item._bond_state == self._bond_state:
                    contains = True
            elif item._int_state == self._int_state:
                if item._bond_state == '#':
                    contains = True
                elif (item._bond_state == '_') & (self._bond_state != '.'):
                    contains = True
                elif item._bond_state == self._bond_state:
                    contains = True
        return contains

    def get_port_name(self) -> str:
        """Returns a string with the port's name."""
        return self._port_name

    def get_port_int_state(self) -> str:
        """Returns a string with the port's internal state."""
        return self._int_state

    def get_port_bond_state(self) -> str:
        """Returns a string with the port's bond state."""
        return self._bond_state


class KappaCounter(KappaSite):
    """"Class for representing counters, pseudo-Kappa sites, e.g. 'c{=5}'."""

    def __init__(self, expression: str):
        self._raw_expression: str
        self._counter_name: str
        self._counter_value: int
        self._kappa_expression: str

        self._raw_expression = expression

        # define patterns that make up a site
        site_name_pat = '([_~][a-zA-Z0-9_~+-]+|[a-zA-Z][a-zA-Z0-9_~+-]*)'
        cnt_state_pat = '{=(\d+)}'
        counter_pat = '^' + site_name_pat + cnt_state_pat + '$'
        # parse the counter
        g = re.match(counter_pat, expression.strip())
        if not g:
            raise CounterParseError('Invalid counter declaration <' + expression + '>')
        # assign capturing groups to variables
        self._counter_name = g.group(1)
        self._counter_value = int(g.group(2))
        # canonicalize the kappa expression
        self._kappa_expression = self._counter_name + '{=' + str(self._counter_value) + '}'

    def get_counter_name(self) -> str:
        """Returns a string with the counter's name."""
        return self._counter_name

    def get_counter_value(self) -> int:
        """Returns an integer with the counter's value."""
        return self._counter_value


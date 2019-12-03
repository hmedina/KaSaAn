#!/usr/bin/env python3

import re
from abc import abstractmethod

from .KappaEntity import KappaEntity
from .KappaError import PortParseError, CounterParseError, PortInclusionError


class KappaSite(KappaEntity):
    @abstractmethod
    def __init__(self):
        pass


class KappaPort(KappaSite):
    """Class for representing traditional Kappa Sites, e.g. 's[3]', 'g[.]{b}', or 'k[_]{#}'."""

    def __init__(self, expression: str):
        self._raw_expression: str
        self._port_name: str
        self._present_bond_state: str
        self._bond_operand: str
        self._future_bond_state: str
        self._present_int_state: str
        self._int_operand: str
        self._future_int_state: str
        self._kappa_expression: str
        self._bond_operation: str

        self._raw_expression = expression
        expression = re.sub(r'\s+|\t+|\n+', '', expression)  # Remove line breaks, tabs, multi-spaces
        # define patterns that make up a site
        ident = r'[_~][a-zA-Z0-9_~+-]+|[a-zA-Z][a-zA-Z0-9_~+-]*'
        port_name_pat = r'(' + ident + r')'
        int_state_pat = r'(?:{(' + ident + r'|#)(?:(/)(' + ident + r'))?})?'
        bnd_state_pat = r'\[(.|_|#|\d+)(?:(/)(.|\d+))?\]'
        port_pat = r'^' + port_name_pat + int_state_pat + bnd_state_pat + int_state_pat + r'$'
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
        # figure out what type of bond operation is being performed
        self._present_bond_state = g.group(5)
        if g.group(6):                                                  # if there's an operation
            self._bond_operand = '/'
            self._future_bond_state = g.group(6)
            self._future_bond_state = g.group(7)
            if g.group(5) == '.':
                if g.group(7) != '.':                                   # ./X
                    self._bond_operation = 'creation'
                else:                                                   # ./.
                    self._bond_operation = ''
            elif g.group(5) == '_':
                if g.group(7) == '.':                                   # _/.
                    self._bond_operation = 'deletion'
                else:                                                   # _/X
                    self._bond_operation = 'unknown'
            elif g.group(5) == '#':                                     # #/?
                self._bond_operation = 'unknown'
            else:
                if g.group(7) == '.':                                   # X/.
                    self._bond_operation = 'deletion'
                else:                                                   # X/Y
                    self._bond_operation = 'swap'
        else:                                                           # if there's no operation
            self._bond_operand = ''
            self._future_bond_state = ''
            self._bond_operation = ''
        # figure out what type of internal state operation is being performed
        if g.group(2):
            self._present_int_state = g.group(2)
            self._int_operand = g.group(3) if g.group(3) else ''
            self._future_int_state = g.group(4) if g.group(4) else ''
        elif g.group(8):
            self._present_int_state = g.group(8)
            self._int_operand = g.group(9) if g.group(9) else ''
            self._future_int_state = g.group(10) if g.group(10) else ''
        else:                                                          # unless specified, will default to wildcard '#'
            self._present_int_state = '#'
            self._int_operand = ''
            self._future_int_state = ''
        # canonicalize the kappa expression
        self._kappa_expression = \
            self._port_name + \
            '[' + self._present_bond_state + self._bond_operand + self._future_bond_state + ']' + \
            '{' + self._present_int_state + self._int_operand + self._future_int_state + '}'

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
        if self._int_operand or self._bond_operand:                 # if self has an operation, issue warning
            raise PortInclusionError('Undefined inclusion test: <' + str(self) + '> has an operation in it.')
        elif item._int_operand or item._bond_operand:               # if item has an operation, issue warning
            raise PortInclusionError('Undefined inclusion test: <' + str(item) + '> has an operation in it.')
        else:
            if self._port_name == item._port_name:
                if item._present_int_state == '#':
                    if item._present_bond_state == '#':
                        contains = True     # [#]{#} in [?]{?}
                    elif self._present_bond_state == '#':
                        contains = True     # [?]{#} in [#]{?}
                    elif (self._present_bond_state == '_') & (item._present_bond_state != '.'):
                        contains = True     # [.]{#} in! [_]{?}
                    elif (item._present_bond_state == '_') & (self._present_bond_state != '.'):
                        contains = True     # [_]{#} in! [.]{?}
                    elif item._present_bond_state == self._present_bond_state:
                        contains = True     # [x]{#} in [x]{?}
                elif self._present_int_state == '#':
                    if item._present_bond_state == '#':
                        contains = True
                    elif self._present_bond_state == '#':
                        contains = True
                    elif (self._present_bond_state == '_') & (item._present_bond_state != '.'):
                        contains = True
                    elif (item._present_bond_state == '_') & (self._present_bond_state != '.'):
                        contains = True
                    elif item._present_bond_state == self._present_bond_state:
                        contains = True
                elif item._present_int_state == self._present_int_state:
                    if item._present_bond_state == '#':
                        contains = True
                    elif self._present_bond_state == '#':
                        contains = True
                    elif (self._present_bond_state == '_') & (item._present_bond_state != '.'):
                        contains = True
                    elif (item._present_bond_state == '_') & (self._present_bond_state != '.'):
                        contains = True
                    elif item._present_bond_state == self._present_bond_state:
                        contains = True
        return contains

    def get_port_name(self) -> str:
        """Returns a string with the port's name."""
        return self._port_name

    def get_port_int_state(self) -> str:
        """Returns a string with the port's internal state."""
        return self._present_int_state + self._int_operand + self._future_int_state

    def get_port_bond_state(self) -> str:
        """Returns a string with the port's bond state."""
        return self._present_bond_state + self._bond_operand + self._future_bond_state

    def get_port_current_bond(self) -> str:
        """Returns a string with the bond state or identifier required for the rule to fire, or the state or identifier
        used in the non-rule expression."""
        return self._present_bond_state

    def get_port_future_bond(self) -> str:
        """Returns a string with the bond state or identifier after rule application, with an empty string for non-rule
        patterns or usages."""
        return self._future_bond_state

    def get_port_current_state(self) -> str:
        """Returns a string with the internal state required for the rule to fire, or the state or identifier
        used in the non-rule expression."""
        return self._present_int_state

    def get_port_future_state(self) -> str:
        """Returns a string with the internal state after rule application, with an empty string for non-rule
        patterns or usages."""
        return self._future_int_state

    def get_port_bond_operation(self) -> str:
        """Returns the operation being performed on this port's bond: creation, deletion, swap, unknown, or an empty
         string for none."""
        return self._bond_operation

    def has_bond_operation(self) -> bool:
        """Returns true if the port has an operation being performed on its bond state."""
        return True if self._bond_operand else False

    def has_state_operation(self) -> bool:
        """Returns true if the port has an operation being performed on its internal state."""
        return True if self._int_operand else False


class KappaCounter(KappaSite):
    """"Class for representing counters, pseudo-Kappa sites, e.g. 'c{=5}'."""

    def __init__(self, expression: str):
        self._raw_expression: str
        self._counter_name: str
        self._current_state: str
        self._counter_operand: str
        self._counter_delta: str
        self._kappa_expression: str

        self._raw_expression = expression
        expression = re.sub(r'\s+|\t+|\n+', '', expression)  # Remove line breaks, tabs, multi-spaces
        # define patterns that make up a site
        site_name_pat = r'([_~][a-zA-Z0-9_~+-]+|[a-zA-Z][a-zA-Z0-9_~+-]*)'
        cnt_state_pat = r'{(>?=\d+)(?:(/)([+-]=\d+))?}'
        counter_pat = r'^' + site_name_pat + cnt_state_pat + r'$'
        # parse the counter
        g = re.match(counter_pat, expression.strip())
        if not g:
            raise CounterParseError('Invalid counter declaration <' + expression + '>')
        # assign capturing groups to variables
        self._counter_name = g.group(1)
        self._current_state = g.group(2)
        self._counter_operand = g.group(3) if g.group(3) else ''
        self._counter_delta = g.group(4) if g.group(4) else ''
        # canonicalize the kappa expression
        self._kappa_expression = \
            self._counter_name + \
            '{' + self._current_state + self._counter_operand + self._counter_delta + '}'

    def get_counter_name(self) -> str:
        """Returns a string with the counter's name."""
        return self._counter_name

    def get_counter_state(self) -> str:
        """Returns a string with the counter's value expression, including the delta if specified."""
        return self._current_state + self._counter_operand + self._counter_delta

    def get_counter_tested_value(self) -> str:
        """Returns a string with the value being tested for the rule's application."""
        return self._current_state

    def get_counter_delta(self) -> str:
        """Returns a string with the delta being applied to the counter's value."""
        return self._counter_delta

    def has_operation(self) -> bool:
        """Returns true if this counter has an operation being performed on it."""
        return True if self._counter_operand else False

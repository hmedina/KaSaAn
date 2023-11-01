#!/usr/bin/env python3
"""Contains `KappaPort` and `KappaCounter`; classes for representing the components of an agent signature."""

import re

from .KappaEntity import KappaEntity
from .KappaError import PortParseError, CounterParseError, PortSatisfactionError


class KappaPort(KappaEntity):
    """
Class for representing traditional Kappa Sites, e.g. `s[3]`, `g[.]{b}`, or `k[_]{#}`.

What is an embedding?
---------------------

The statement 'A contains B', or 'A in B', we interpret as meaning 'A embeds in B', specifically 'A satisfied by B',
akin to saying 'B matches A', where 'match' is the inverse mapping to 'embed'. See `KappaPort.embeds_in` and
`KappaPort.matches_to`
Besides typing (e.g. can't satisfy `KappaPort` with a `KappaCounter`), this satisfaction requires three true components,
the name, the internal state, and the bond state.

Site names are only satisfied by equality of their string representation.

Internal state truth table
--------------------------

* `s{#} in s{#}` <= True
* `s{a} in s{#}` <= False
* `s{#} in s{a}` <= True
* `s{a} in s{a}` <= True
* `s{a} in s{b}` <= False

Bond state truth table
----------------------

* `s[#] in [#]` <= True
* `s[_] in [#]` <= False
* `s[.] in [#]` <= False
* `s[8] in [#]` <= False
* `s[#] in [_]` <= True
* `s[_] in [_]` <= True
* `s[.] in [_]` <= False
* `s[7] in [_]` <= True
* `s[#] in [.]` <= True
* `s[_] in [.]` <= False
* `s[.] in [.]` <= True
* `s[6] in [.]` <= False
* `s[#] in [5]` <= True
* `s[_] in [5]` <= True
* `s[.] in [5]` <= False
* `s[5] in [5]` <= True
* `s[3] in [4]` <= False
    """

    # define patterns that make up a port
    __ident = r'[_~][a-zA-Z0-9_~+-]+|[a-zA-Z][a-zA-Z0-9_~+-]*'
    __port_name_pat = r'(' + __ident + r')'
    __int_state_pat = r'(?:{(' + __ident + r'|#)(?:(/)(' + __ident + r'))?})?'
    __bnd_state_pat = r'\[(.|_|#|\d+)(?:(/)(.|\d+))?\]'
    __port_pat = r'^' + __port_name_pat + __int_state_pat + __bnd_state_pat + __int_state_pat + r'$'
    __port_pat_re = re.compile(__port_pat)

    def __init__(self, expression: str):
        self._raw_expression: str
        self.name: str
        self._present_bond_state: str
        self._bond_operand: str
        self._future_bond_state: str
        self._present_int_state: str
        self._int_operand: str
        self._future_int_state: str
        self._kappa_expression: str
        self._bond_operation: str

        self._raw_expression = expression
        # Remove line breaks, tabs, multi-spaces
        expression = self._whitespace_re.sub('', expression)
        # parse assuming full site declaration, with bond state declared
        g = self.__port_pat_re.match(expression.strip())
        # if that fails, try parsing with bond state explicitly declared as a wildcard
        if not g:
            g = self.__port_pat_re.match(expression.strip() + '[#]')
        # if that fails, throw an error
        if not g:
            raise PortParseError('Invalid port declaration <' + expression + '>')
        # assuming it parsed, assign capturing groups to variables
        self.name = g.group(1)
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
            self.name + \
            '[' + self._present_bond_state + self._bond_operand + self._future_bond_state + ']' + \
            '{' + self._present_int_state + self._int_operand + self._future_int_state + '}'

    def __contains__(self, query) -> bool:
        """"""

        # we can't satisfy ports with counters
        if type(query) is KappaCounter:
            raise PortParseError('Can not check for containment of supplied counter <' + query +
                                 '> in port <' + self._kappa_expression + '>')
        # make it a KappaPort if it's not one already
        elif not type(query) is KappaPort:
            query = KappaPort(query)
        # check if item is satisfied by self, Kappa-wise
        if self._int_operand or self._bond_operand:                     # if self has an operation, issue warning
            raise PortSatisfactionError('Undefined satisfaction test: <' + str(self) + '> has an operation in it.')
        elif query._int_operand or query._bond_operand:                 # if item has an operation, issue warning
            raise PortSatisfactionError('Undefined satisfaction test: <' + str(query) + '> has an operation in it.')
        else:
            satisfied = False
            # site name satisfied?
            if self.name == query.name:
                # first check if internal state satisfied,
                # then check if bond state satisfied
                if query._present_int_state == '#':
                    satisfied = _bond_state_satisfaction(query_port=query, target_port=self)
                elif query._present_int_state == self._present_int_state:
                    satisfied = _bond_state_satisfaction(query_port=query, target_port=self)
        return satisfied

    def get_port_name(self) -> str:
        """Returns a string with the port's name."""
        return self.name

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
        """Returns the operation being performed on this port's bond: `creation`, `deletion`, `swap`, `unknown`, or
         an empty string for none."""
        return self._bond_operation

    def has_bond_operation(self) -> bool:
        """Returns `true` if the port has an operation being performed on its bond state."""
        return True if self._bond_operand else False

    def has_state_operation(self) -> bool:
        """Returns `true` if the port has an operation being performed on its internal state."""
        return True if self._int_operand else False

    def embeds_in(self, target) -> bool:
        """Does the self entity embed in, is satisfied by, the target entity? The inverse mapping of an embedding is the
        matching, see `KappaPort.matches_to`."""
        return self in target

    def matches_to(self, query) -> bool:
        """Does the self entity match to the query entity, does it satisfy it's requirements?  The inverse mapping of a
        matching is the embedding, see `KappaPort.embeds_in`."""
        return query in self


class KappaCounter(KappaEntity):
    """Class for representing counters, pseudo-Kappa sites, e.g. `c{=5}`."""

    # define patterns that make up a counter
    __site_name_pat = r'([_~][a-zA-Z0-9_~+-]+|[a-zA-Z][a-zA-Z0-9_~+-]*)'
    __cnt_state_pat = r'{(>?=\d+)(?:(/)([+-]=\d+))?}'
    __counter_pat = r'^' + __site_name_pat + __cnt_state_pat + r'$'
    __counter_pat_re = re.compile(__counter_pat)

    def __init__(self, expression: str):
        self._raw_expression: str
        self.name: str
        self._current_state: str
        self._counter_operand: str
        self._counter_delta: str
        self._kappa_expression: str

        self._raw_expression = expression
        expression = self._whitespace_re.sub('', expression)     # Remove line breaks, tabs, multi-spaces
        # parse the counter
        g = self.__counter_pat_re.match(expression.strip())
        if not g:
            raise CounterParseError('Invalid counter declaration <' + expression + '>')
        # assign capturing groups to variables
        self.name = g.group(1)
        self._current_state = g.group(2)
        self._counter_operand = g.group(3) if g.group(3) else ''
        self._counter_delta = g.group(4) if g.group(4) else ''
        # canonicalize the kappa expression
        self._kappa_expression = \
            self.name + \
            '{' + self._current_state + self._counter_operand + self._counter_delta + '}'

    def get_counter_name(self) -> str:
        """Returns a string with the counter's name."""
        return self.name

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


def _bond_state_satisfaction(query_port: KappaPort, target_port: KappaPort) -> bool:
    """Is the query string satisfied by the target string, when read as bond states?"""
    if query_port.get_port_current_bond() == '.':
        satisfied = True if target_port.get_port_current_bond() == '.' else False
    elif query_port.get_port_current_bond() == '_':
        satisfied = True if target_port.get_port_current_bond() not in ['.', '#'] else False
    elif query_port.get_port_current_bond() == '#':
        satisfied = True
    else:
        satisfied = True if target_port.get_port_current_bond() == query_port.get_port_current_bond() else False
    return satisfied

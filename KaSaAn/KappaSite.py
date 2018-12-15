#! /usr/bin/python3
import re
from functools import total_ordering
from .KappaError import SiteParseError


class KappaSite:
    """Class for representing Kappa sites; e.g. 's[3]', 'g[.]{b}', 'k[_]{#}'."""

    def __init__(self, expression: str):
        self.raw_expression: str
        self.site_name: str
        self.bond_state: str
        self.int_state: str
        self.kappa_expression: str

        self.raw_expression = expression
        # parse assuming full site declaration, with bond state declared
        g = re.match('^([a-zA-Z]\w*)(?:{(\w+|#)})?\[(.|_|#|\d+)\](?:{(\w+|#)})?$', self.raw_expression.strip())
        # if that fails, try parsing with bond state explicitly declared as a wildcard
        if not g:
            g = re.match('^([a-zA-Z]\w*)(?:{(\w+|#)})?\[(.|_|#|\d+)\](?:{(\w+|#)})?$', self.raw_expression.strip() + '[#]')
        # if that fails, throw an error
        if not g:
            raise SiteParseError('Invalid site declaration <' + expression + '>')
        # assuming we survived, assign stuff to variables
        self.site_name = g.group(1)
        self.bond_state = g.group(3)
        # for internal states, unless specified, it will default to wildcard '#'
        if g.group(2):
            self.int_state = g.group(2)
        elif g.group(4):
            self.int_state = g.group(4)
        else:
            self.int_state = '#'
        # canonicalize the kappa expression
        self.kappa_expression = self.site_name + '[' + self.bond_state + ']{' + self.int_state + '}'

    def __repr__(self) -> str:
        return 'KappaSite("{0}")'.format(self.kappa_expression)

    def __str__(self) -> str:
        return self.kappa_expression

    def __hash__(self) -> int:
        return hash(self.kappa_expression)

    def __eq__(self, other) -> bool:
        # make it a KappaSite if it's not one already
        if not type(other) is KappaSite:
            other = KappaSite(other)
        # as kappa_expressions have been canonicalized, they're sufficient for equality testing
        return True if self.kappa_expression == other.kappa_expression else False

    def __lt__(self, other) -> bool:
        # make it a KappaSite if it's not one already
        if not type(other) is KappaSite:
            other = KappaSite(other)
        # as kappa_expression have been canonicalized, they're sufficient for comparison testing
        return True if self.kappa_expression < other.kappa_expression else False

    @total_ordering

    def __contains__(self, item) -> bool:
        # make it a KappaSite if it's not one already
        if not type(item) is KappaSite:
            item = KappaSite(item)
        # check if item is in self, Kappa-wise
        contains = False
        if self.site_name == item.site_name:
            if item.int_state == '#':
                if item.bond_state == '#':
                    contains = True
                elif (item.bond_state == '_') & (self.bond_state != '.'):
                    contains = True
                elif item.bond_state == self.bond_state:
                    contains = True
            elif item.int_state == self.int_state:
                if item.bond_state == '#':
                    contains = True
                elif (item.bond_state == '_') & (self.bond_state != '.'):
                    contains = True
                elif item.bond_state == self.bond_state:
                    contains = True
        return contains

    def get_site_name(self) -> str:
        """Returns a string with the name of the site."""
        return self.site_name

    def get_site_internal_state(self) -> str:
        """Returns a string with the site's internal state."""
        return self.int_state

    def get_site_bond_state(self) -> str:
        """Returns a string with the site's bond state."""
        return self.bond_state

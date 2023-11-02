#!/usr/bin/env python3
"""Contains the abstract base class from which all others are derived."""

import re

from abc import ABC, abstractmethod
from functools import total_ordering

from .KappaError import KappaEqualtiyError


@total_ordering
class KappaEntity(ABC):
    """Abstract base class for Kappa entities. It should not be invoked directly. Contains boiler-plate code used
    by child classes."""

    _whitespace_re = re.compile(r'\s+|\t+|\n+')  # used for string cleanup and sanitization

    @abstractmethod
    def __init__(self):
        self._kappa_expression = ''
        pass

    def __repr__(self) -> str:
        return '{0}("{1}")'.format(self.__class__.__name__, self._kappa_expression)

    def __str__(self) -> str:
        return self._kappa_expression

    def __hash__(self) -> int:
        return hash(self._kappa_expression)

    def __eq__(self, other) -> bool:
        # as the kappa_expression has been canonicalized, it is sufficient for equality testing
        # the bulk of this method is just type-checking
        if isinstance(other, str):
            # if other is a string, make it into an instance of my class
            other = self.__class__(other)
            return True if self._kappa_expression == other._kappa_expression else False
        elif issubclass(other.__class__, KappaEntity):
            if type(other) is type(self):
                # if comparing two of the same class & subclass
                return True if self._kappa_expression == other._kappa_expression else False
            else:
                # if comparing, say Agents and Complexes, same parent class, but different classes
                raise KappaEqualtiyError(
                    'Can not compare <' + str(self) + '> to <' + str(other) + '> as they have different classes.')
        else:
            # if comparing some other type to a kappa entity
            raise ValueError(
                'Can not compare <' + str(self) + '> to <' + str(other) + '> as the latter is not a compatible class')

    def __lt__(self, other) -> bool:
        # make it a Kappa-whatever-this-is if it's not one already
        if type(other) is not type(self):
            other = self.__class__(other)
        # as kappa_expression have been canonicalized, they're sufficient for comparison testing (i.e. alphabetically)
        return True if self._kappa_expression < other._kappa_expression else False

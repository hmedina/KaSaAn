#! /usr/local/bin/python3

from abc import ABC, abstractmethod
from functools import total_ordering


@total_ordering
class KappaEntity(ABC):
    """Abstract base class for Kappa entities. It should not be invoked directly. Contains boiler-plate code used
    by child classes."""

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
        # make it a Kappa-whatever-this-is if it's not one already
        if not type(other) is type(self):
            other = self.__class__(other)
        # as kappa_expressions have been canonicalized, they're sufficient for equality testing
        return True if self._kappa_expression == other._kappa_expression else False

    def __lt__(self, other) -> bool:
        # make it a Kappa-whatever-this-is if it's not one already
        if not type(other) is type(self):
            other = self.__class__(other)
        # as kappa_expression have been canonicalized, they're sufficient for comparison testing (i.e. alphabetically)
        return True if self._kappa_expression < other._kappa_expression else False

#!/usr/bin/env python3

from .KappaEntity import KappaEntity


class KappaBond(KappaEntity):
    """Class for representing kappa typed bonds. These are oriented, to guarantee an agent can only have at most
    one of each type of bond; consider `Bob(tail[1]), Bob(head[1], tail[2]), Bob(head[2])`; the middle Bob will have
    two bonds, one of each type `Bob.tail..head.Bob` and `Bob.head..tail.Bob`. Equality testing respects
    orientation, whereas inclusion testing ignores orientation."""

    def __init__(self, agent_one: str, site_one: str, agent_two: str, site_two: str):
        self._kappa_expression: str
        self.agent_one = agent_one
        self.agent_two = agent_two
        self.site_one = site_one
        self.site_two = site_two
        self.stub_one = (agent_one, site_one)
        self.stub_two = (agent_two, site_two)
        # canonicalize expression
        self._kappa_expression = agent_one + '.' + site_one + '..' + site_two + '.' + agent_two

    def __repr__(self) -> str:
        return '{0}{1}'.format(self.__class__.__name__, self.stub_one + self.stub_two)

    def __eq__(self, other) -> bool:
        if type(other) is not KappaBond:
            other = KappaBond(*other)
        return self._kappa_expression == other._kappa_expression

    def __contains__(self, other) -> bool:
        if type(other) is not KappaBond:
            other = KappaBond(*other)
        if (self.stub_one == other.stub_one and self.stub_two == other.stub_two) or \
                (self.stub_one == other.stub_two and self.stub_two == other.stub_one):
            return True
        else:
            return False

    def reverse(self):
        """Returns a KappaBond object with the agent & site pairs in reverse.
        >>> from KaSaAn.core import KappaBond
        >>> foo = KappaBond('Bob', 'head', 'Bob', 'tail')
        >>> foo.reverse()
        KappaBond('Bob', 'tail', 'Bob', 'head')
        """
        return KappaBond(self.agent_two, self.site_two, self.agent_one, self.site_one)

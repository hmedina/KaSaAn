#! /usr/bin/python3


class KappaError(Exception):
    """Base class for exceptions in this module."""
    def __init__(self, message):
        self.message = message


class CounterParseError(KappaError):
    """Exception raised when failing to parse a counter site."""


class PortParseError(KappaError):
    """Exception raised when failing to parse a port site."""


class AgentParseError(KappaError):
    """Exception raised when failing to parse an agent."""


class ComplexParseError(KappaError):
    """Exception raised when failing to parse a complex."""


class SnapshotParseError(KappaError):
    """Exception raised when failing to parse a snapshot."""

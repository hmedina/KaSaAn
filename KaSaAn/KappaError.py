#!/usr/bin/env python3


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


class TokenParseError(KappaError):
    """Exception raised when failing to parse a token."""


class ComplexParseError(KappaError):
    """Exception raised when failing to parse a complex."""


class SnapshotParseError(KappaError):
    """Exception class for error when parsing snapshots."""


class SnapshotAgentParseError(SnapshotParseError):
    """Exception raised when failing to parse a line in a snapshot that should contain agents."""


class SnapshotTokenParseError(SnapshotParseError):
    """Exception raised when failing to parse a line in a snapshot that should contain tokens."""
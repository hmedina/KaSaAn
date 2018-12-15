#! /usr/bin/python3


class KappaError(Exception):
    """Base class for exceptions in this module."""
    pass


class SiteParseError(KappaError):
    """Exception raised when failing to parse a site."""
    def __init__(self, message):
        self.message = message


class AgentParseError(KappaError):
    """Exception raised when failing to parse an agent."""
    def __init__(self, message):
        self.message = message


class ComplexParseError(KappaError):
    """Exception raised when failing to parse a complex."""
    def __init__(self, message):
        self.message = message

class SnapshotParseError(KappaError):
    """Exception raised when failing to parse a snapshot."""
    def __init__(self, message):
        self.message = message

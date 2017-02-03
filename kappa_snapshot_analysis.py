#! python.exe
import re


class KappaComplex:
    """Class for representing & manipulating Kappa complexes."""

    def __init__(self, kappa_expression):
        self.kappa_expression = kappa_expression

    def get_number_of_agent(self, agent_expression):
        """Prints the number of times a given agent appears in the complex. It supports specifying parts of the
        signature for the agent, specifically state information. I.e. looking for `A(s~x)` is supported."""
        matches = re.match('([a-zA-Z]+\w*)\(([\w!,~]*)\)', agent_expression)
        agent_name = matches.group(1)
        agent_signature = matches.group(2)
        pattern = agent_name + '\([\w!,~]*' + agent_signature + '[\w!,~]*\)'
        matches = re.findall(pattern, self.kappa_expression)
        print(len(matches))

    def get_constituent_agents(self):
        """Prints the set of agents that make up the complex."""
        matches = re.findall('([a-zA-Z]+\w*)\([\w!,~]*\)', self.kappa_expression)
        agents = set(matches)
        print(agents)

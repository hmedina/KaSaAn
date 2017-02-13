#! python.exe
import re


class KappaComplex:
    """Class for representing  Kappa complexes. I.e. 'A(b!1),B(a!1,c!2),C(b!2,a!3),A(c!3,s~x)'. Notice these must be
    connected components. E.g. each line of a kappa snapshot is a KappaComplex."""

    ka_nom_expr = '[a-zA-Z]+\w*'
    ka_sig_expr = '[\w!,~\s]*'

    def __init__(self, kappa_expression):
        self.kappa_expression = kappa_expression

    def get_number_of_given_agent(self, kappa_query):
        """Returns the number of times a given agent appears in the complex. It supports specifying parts of the
        signature for the agent, specifically state information. I.e. looking for 'A(s~x)' is supported."""

        # Get agent name & signature, and make sure input is a valid kappa expression
        matches = re.match('(' + self.ka_nom_expr + ')\((' + self.ka_sig_expr + ')\)', kappa_query)
        assert matches, 'Query is not a valid kappa expression >' + kappa_query + '< forgot parenthesis?'
        query_name = matches.group(1)
        query_signature = matches.group(2)

        # Pad known signature with pattern to match against user unmentioned sites stated in snapshot
        pattern = query_name + '\(' + self.ka_sig_expr + query_signature + self.ka_sig_expr + '\)'
        matches = re.findall(pattern, self.kappa_expression)
        return len(matches)

    def get_number_of_bonds(self):
        """Returns the number of bonds in the complex."""
        matches = re.findall('!\d+', self.kappa_expression)
        return int(len(matches) / 2)

    def get_size_of_complex(self):
        """Returns the size, in agents, of this complex. This works by counting the number of agent signatures with
        their open/close parentheses."""
        matches = re.findall('\(' + self.ka_sig_expr + '\)', self.kappa_expression)
        return int(len(matches))

    def get_constituent_agents(self):
        """Returns the set of agents that make up the complex."""
        matches = re.findall('(' + self.ka_nom_expr + ')\(' + self.ka_sig_expr + '\)', self.kappa_expression)
        agents = set(matches)
        return agents


class KappaSnapshot:
    raise NotImplemented

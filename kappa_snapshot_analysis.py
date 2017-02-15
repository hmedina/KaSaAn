#! python.exe
import re


class KappaComplex:
    """Class for representing Kappa complexes. I.e. 'A(b!1),B(a!1,c!2),C(b!2,a!3),A(c!3,s~x)'. Notice these must be
    connected components. E.g. each line of a kappa snapshot contains a KappaComplex."""

    def __init__(self, kappa_expression):
        self.kappa_expression = kappa_expression

    def get_number_of_given_agent(self, kappa_query):
        """Returns the number of times a given agent appears in the complex. It supports specifying parts of the
        signature for the agent, specifically state information. I.e. looking for 'A(s~x)' is supported."""

        # Get agent name & signature, and make sure input is a valid kappa expression
        matches = re.match('([a-zA-Z]+\w*)\(\)', kappa_query)
        assert matches, 'Invalid query >' + kappa_query + '<, only agent name + parentheses "A()" accepted.'
        query_name = matches.group(1)

        # Pad known signature with pattern to match against user unmentioned sites stated in snapshot
        matches = re.findall(query_name + '\([^)]*\)', self.kappa_expression)
        return len(matches)

    def get_number_of_bonds(self):
        """Returns the number of bonds in the complex."""
        matches = re.findall('!\d+', self.kappa_expression)
        return int(len(matches) / 2)

    def get_size_of_complex(self):
        """Returns the size, in agents, of this complex. This works by counting the number of agent signatures with
        their open/close parentheses."""
        matches = re.findall('\([^)]*\)', self.kappa_expression)
        return int(len(matches))

    def get_constituent_agents(self):
        """Returns the set of agents that make up the complex."""
        matches = re.findall('([a-zA-Z]+\w*)\([^)]*\)', self.kappa_expression)
        agents = set(matches)
        return agents


class KappaSnapshot:
    """Class for representing Kappa snapshots. A snapshot is represented as a dictionary, where the kappa expression
    serves as the key, and the abundance serves as the value. Many of the methods for this class are simple re-namings
     of the Dict() class', but with more informative names for kappa entities."""

    def __init__(self, snapshot_file_name):
        self.snapshot = dict()
        with open(snapshot_file_name, 'r') as kf:
            for line in kf:
                if (line[0] != '#') & (line != '\n'):
                    kappa_dump = re.search('^%init:\s(\d+)\s(.+)', line)
                    complex_abundance = int(kappa_dump.group(1))
                    complex_expression = KappaComplex(kappa_dump.group(2))
                    self.snapshot[complex_expression] = complex_abundance

    def get_all_complexes(self):
        """Returns a list with all the complexes in the snapshot. These complexes are not strings, but belong to class
        KappaComplex."""
        return list(self.snapshot.keys())

    def get_all_abundances(self):
        """Returns a list with all the abundances declared in the snapshot. These are integer values."""
        return list(self.snapshot.values())

    def get_all_complexes_and_abundances(self):
        """Returns a dictionary where the keys belong to class KappaComplex and the values are the abundances of the
        corresponding complex."""
        return list(self.snapshot.items())

    def get_complexes_with_abundance(self, query_abundance):
        """Allows one to get the list of complexes present at a query abundance. For example, get all the dimers."""
        result_complexes = []
        for complex_expression, complex_abundance in self.snapshot.items():
            if query_abundance == complex_abundance:
                result_complexes.append(complex_expression)
        return result_complexes

    def get_largest_complex(self):
        """Returns the largest complex, measured in number of constituting agents, found in the snapshot."""
        max_size = 0
        largest_complex = None
        for complex_expression in self.get_all_complexes():
            current_size = complex_expression.get_size_of_complex()
            if current_size > max_size:
                largest_complex = complex_expression
                max_size = current_size
        return largest_complex

    def get_most_abundant_complexes(self):
        """Returns the list of complexes found to be the most abundant. These could be the monomers for example."""
        max_abundance = max(self.get_all_abundances())
        return self.get_complexes_with_abundance(max_abundance)

    def get_size_distribution(self):
        """Returns a dictionary where the key is the size of a complex and the value is the amount of complexes with
        that size. For example, {1:3, 4:5} indicates the mixture contains only three monomers and five tetramers."""
        size_dist = dict()
        for complex_expression, complex_abundance in self.get_all_complexes_and_abundances():
            current_size = complex_expression.get_size_of_complex()
            if current_size in size_dist:
                size_dist[current_size] += complex_abundance
            else:
                size_dist[current_size] = complex_abundance
        return size_dist

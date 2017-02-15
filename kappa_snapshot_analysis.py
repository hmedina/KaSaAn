#! python.exe
import re
import matplotlib.pyplot


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
        """Returns a list of KappaComplexes with all the complexes in the snapshot."""
        return list(self.snapshot.keys())

    def get_all_abundances(self):
        """Returns a list of integers with all the abundances in the snapshot."""
        return list(self.snapshot.values())

    def get_all_complexes_and_abundances(self):
        """Returns a dictionary where the keys are KappaComplexes and the values are int abundances of the
        corresponding complex."""
        return list(self.snapshot.items())

    def get_complexes_with_abundance(self, query_abundance):
        """Returns a list of KappaComplexes present in the snapshot at the query abundance. For example, get all
        elements present in single copy."""
        result_complexes = []
        for complex_expression, complex_abundance in self.get_all_complexes_and_abundances():
            if query_abundance == complex_abundance:
                result_complexes.append(complex_expression)
        return result_complexes

    def get_complexes_of_size(self, query_size):
        """Returns the list of complexes that are of the query size. For example, get all the dimers."""
        result_complexes = []
        for complex_expression, complex_abundance in self.get_all_complexes_and_abundances():
            if query_size == complex_expression.get_size_of_complex():
                result_complexes.append(complex_expression)
        return result_complexes

    def get_largest_complexes(self):
        """Returns a list of KappaComplexes with the largest complexes, measured in number of constituting agents."""
        max_known_size = 0
        for complex_expression in self.get_all_complexes():
            current_size = complex_expression.get_size_of_complex()
            if current_size > max_known_size:
                max_known_size = current_size
        return self.get_complexes_of_size(max_known_size)

    def get_smallest_complexes(self):
        """Returns a list of KappaComplexes with the smallest complexes, measured in number of constituting agents."""
        min_known_size = self.get_largest_complexes()[0].get_size_of_complex() + 1
        for complex_expression in self.get_all_complexes():
            current_size = complex_expression.get_size_of_complex()
            if current_size < min_known_size:
                min_known_size = current_size
        return self.get_complexes_of_size(min_known_size)

    def get_most_abundant_complexes(self):
        """Returns the list of complexes found to be the most abundant. These could be the monomers for example."""
        max_abundance = max(self.get_all_abundances())
        return self.get_complexes_with_abundance(max_abundance)

    def get_least_abundant_complexes(self):
        """Returns the list of complexes found to be the least abundant. For example, this would be the giant component,
        or the set of largest entities."""
        min_abundance = min(self.get_all_abundances())
        return self.get_complexes_with_abundance(min_abundance)

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

    def plot_size_distribution(self):
        """"Plots the size distribution of complexes in the snapshot."""
        size_distribution = self.get_size_distribution()
        polymer_sizes = list(size_distribution.keys())
        polymer_abundances = list(size_distribution.values())
        matplotlib.pyplot.plot(polymer_sizes, polymer_abundances)

        matplotlib.pyplot.xlabel('Complex size')
        matplotlib.pyplot.ylabel('Complex abundance')
        matplotlib.pyplot.title('Distribution of complex sizes')
        matplotlib.pyplot.grid(True)
        matplotlib.pyplot.show()

    def plot_mass_distribution(self):
        """Plots the mass distribution of protomers in the snapshot: a monomer counts as one, a dimer as two, a trimer
        as three, and so on. Thus, 5 trimers have a mass of 15."""
        size_distribution = self.get_size_distribution()
        polymer_sizes = list(size_distribution.keys())
        polymer_abundances = list(size_distribution.values())
        polymer_mass = [a * b for a, b in zip(polymer_sizes, polymer_abundances)]
        matplotlib.pyplot.plot(polymer_sizes, polymer_mass)

        matplotlib.pyplot.xlabel('Complex size')
        matplotlib.pyplot.ylabel('Complex mass')
        matplotlib.pyplot.title('Distribution of protomer mass in complexes')
        matplotlib.pyplot.grid(True)
        matplotlib.pyplot.show()

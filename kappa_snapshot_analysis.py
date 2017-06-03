#! /usr/bin/python3
import re
import matplotlib.pyplot


def site_contains_site(host, query):
    """Helper function for the KappaAgent class."""
    h_matches = re.match('^([a-zA-Z]\w*)(~\w+)?(!\d+)?', host)
    h_site_name = h_matches.group(1) if h_matches.group(1) else None
    h_site_state = h_matches.group(2) if h_matches.group(2) else None
    h_site_bond = h_matches.group(3) if h_matches.group(3) else None

    q_matches = re.match('^([a-zA-Z]\w*)([?~]\w*)?([?!][_\d]*)?', query)
    q_site_name = q_matches.group(1) if q_matches.group(1) else None
    q_site_state = q_matches.group(2) if q_matches.group(2) else None
    q_site_bond = q_matches.group(3) if q_matches.group(3) else None

    sites_match = False
    if q_site_name == h_site_name:
        if q_site_state == '?':
            sites_match = True
        elif q_site_state == h_site_state:
            if q_site_bond == '?':
                sites_match = True
            elif q_site_bond == h_site_bond:
                sites_match = True
            elif q_site_bond == '!_' and h_site_bond:
                sites_match = True
    return sites_match


class KappaAgent:
    """Class for representing Kappa gents. I.e. 'A(b!1)' or 'A(s~a,a!_,b)'."""
    def __init__(self, kappa_expression):
        # Remove spaces in the expression
        kappa_expression = kappa_expression.replace(' ', '')

        # Check if kappa expression is valid
        matches = re.match('([a-zA-Z]\w*)\(([^)]*)\)', kappa_expression)
        assert matches, 'Invalid kappa expression >' + kappa_expression + '<'

        # Assign results to variables
        self.kappa_expression = kappa_expression
        self.agent_name = matches.group(1)
        if matches.group(2) == '':
            self.agent_signature = []
        else:
            self.agent_signature = matches.group(2).split(',')

    def contains_site(self, query_site):
        """Return true or false, depending on whether the agent contains the query site."""
        matches = False
        for s_site in self.agent_signature:
            if site_contains_site(s_site, query_site):
                matches = True
                break
        return matches

    def get_bond_identifiers(self):
        """Return the list of bonds ending/starting at this agent, e.g. for 'A(a,b!1,c!2,d~a)' these would be the list
        of ['1','2']."""
        agent_bonds = []
        for item in self.agent_signature:
            matches = re.match('[a-zA-Z]\w*!(\d+)', item)
            if matches:
                agent_bonds.append(matches.group(1))
        return agent_bonds


class KappaComplex:
    """Class for representing Kappa complexes. I.e. 'A(b!1),B(a!1,c!2),C(b!2,a!3),A(c!3,s~x)'. Notice these must be
    connected components. E.g. each line of a kappa snapshot contains a KappaComplex."""

    def __init__(self, kappa_expression):
        """The constructor also removes spaces from the expression."""
        self.kappa_expression = kappa_expression.replace(' ', '')

    def get_number_of_bonds(self):
        """Returns the number of bonds in the complex."""
        matches = re.findall('!\d+', self.kappa_expression)
        return int(len(matches) / 2)

    def get_size_of_complex(self):
        """Returns the size, in agents, of this complex. This works by counting the number of agent signatures with
        their open/close parentheses."""
        matches = re.findall('\([^)]*\)', self.kappa_expression)
        return int(len(matches))

    def get_agent_types(self):
        """Returns the set of agents that make up the complex."""
        matches = re.findall('([a-zA-Z]\w*)\([^)]*\)', self.kappa_expression)
        agents = set(matches)
        return agents

    def get_agents(self):
        """Returns a list of KappaAgents of the agents in this complex."""
        agent_list = self.kappa_expression.split('),')
        agent_list = [KappaAgent(item + ')') for item in agent_list]
        return agent_list

    def get_number_of_embeddings_of_agent(self, query):
        """Returns the number of embeddings the query agent has on the KappaComplex. Does not follow bonds,
        so effectively the query must be a single-agent."""
        kappa_query = KappaComplex(query)
        match_number = 0
        # First, we iterate over the agents in our complex
        for s_agent in self.get_agents():
            # Secondly, we iterate over the agents in the query
            for q_agent in kappa_query.get_agents():
                # If agent names match, we move to evaluate sites
                if s_agent.agent_name == q_agent.agent_name:
                    match_score = 0
                    # Thirdly, we iterate over the query's sites
                    for q_site in q_agent.agent_signature:
                        if s_agent.contains_site(q_site):
                            match_score += 1
                    # This counter keeps track of how many fully-matched queries we've embedded
                    if match_score == len(q_agent.agent_signature):
                        match_number += 1
        return match_number

    def get_number_of_embeddings_of_complex(self, query):
        """Returns the number of embedding the query complex has on the KappaComplex."""
        raise NotImplemented


class KappaSnapshot:
    """Class for representing Kappa snapshots. A snapshot is represented as a dictionary, where the kappa expression
    serves as the key, and the abundance serves as the value. Many of the methods for this class are simple re-namings
     of the Dict() class', but with more informative names for kappa entities."""

    def __init__(self, snapshot_file_name):
        self.snapshot = dict()
        with open(snapshot_file_name, 'r') as kf:
            for line in kf:
                if line[0:6] == '%init:':
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
        """Returns a list of tuples, where the first element is a KappaComplex and the second is an int with the
        abundance of the corresponding complex."""
        return list(self.snapshot.items())

    def get_total_mass(self):
        """Returns an int with the total mass of the snapshot, measured in number of agents."""
        total_mass = 0
        for i_complex, i_abundance in self.get_all_complexes_and_abundances():
            total_mass += i_complex.get_size_of_complex() * i_abundance
        return total_mass

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
        # Cast into a list of tuples from a dictionary
        size_distribution = size_distribution.items()

        # Sort the list by polymer size & get x,y vectors for plotting
        sorted_size_distribution = sorted(size_distribution, key=lambda x: x[0])
        polymer_sizes = [item[0] for item in sorted_size_distribution]
        polymer_abundances = [item[1] for item in sorted_size_distribution]

        # Plot and annotate axes
        matplotlib.pyplot.plot(polymer_sizes, polymer_abundances, '.')
        matplotlib.pyplot.xlabel('Complex size')
        matplotlib.pyplot.ylabel('Complex abundance')
        matplotlib.pyplot.title('Distribution of complex sizes')
        matplotlib.pyplot.grid(True)
        matplotlib.pyplot.show()

    def plot_mass_distribution(self):
        """Plots the mass distribution of protomers in the snapshot: a monomer counts as one, a dimer as two, a trimer
        as three, and so on. Thus, five trimers have a mass of 15."""
        size_distribution = self.get_size_distribution()
        # Cast into a list of tuples from a dictionary
        size_distribution = size_distribution.items()

        # Sort the list by polymer size & get x,y vectors for plotting
        sorted_size_distribution = sorted(size_distribution, key=lambda x: x[0])
        polymer_sizes = [item[0] for item in sorted_size_distribution]
        polymer_mass = [item[1] * item[0] for item in sorted_size_distribution]

        # Plot and annotate axes
        matplotlib.pyplot.plot(polymer_sizes, polymer_mass, '.')
        matplotlib.pyplot.xlabel('Complex size')
        matplotlib.pyplot.ylabel('Complex mass')
        matplotlib.pyplot.title('Distribution of protomer mass in complexes')
        matplotlib.pyplot.grid(True)
        matplotlib.pyplot.show()

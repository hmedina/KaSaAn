#! /usr/bin/python3

import re
from .KappaComplex import KappaComplex


class KappaSnapshot:
    """Class for representing Kappa snapshots. A snapshot is represented as a dictionary, where the kappa expression
    serves as the key, and the abundance serves as the value. Many of the methods for this class are simple re-namings
     of the Dict() class', but with more informative names for kappa entities."""

    def __init__(self, snapshot_file_name):
        self.file_name = snapshot_file_name
        self.snapshot = dict()
        building_complex = False
        # Due to the way Kappa4 breaks snapshot files into many lines, the bulk of this parsing operation is just to
        # reconstruct broken-up complexes. I've divided the operation into two modes, signaled by the boolean
        # <<building_complex>>. When true, the line reads append to generate an expression, eventually setting the flag
        # back to false.

        with open(snapshot_file_name, 'r') as kf:
            for line in kf:

                if building_complex:
                    # Determine if this line is the continuation of a complex (i.e. starts in spaces, ends in a comma)
                    if re.search('^\s\s.+\),$', line):
                        kappa_dump = re.search('^\s(\s.+\),)$', line)
                        complex_expression += kappa_dump.group(1)

                    # Determine if this line is the termination fo a complex (i.e. starts in spaces, ends in a closing
                    # parenthesis).
                    elif re.search('^\s\s.+\)$', line):
                        kappa_dump = re.search('^\s(\s.+\))$', line)
                        complex_expression += kappa_dump.group(1)
                        # Transform the string into a KappaComplex
                        complex_expression = KappaComplex(complex_expression)
                        self.snapshot[complex_expression] = complex_abundance
                        building_complex = False

                else:
                    # Determine if this line is the beginning of a complex (i.e. ends in a comma)
                    if re.search('^%init:\s\d+\s/\*.+\*/?.+\),$', line):
                        kappa_dump = re.search('^%init:\s(\d+)\s(/\*.+\*/)?\s(.+\),)', line)
                        complex_abundance = int(kappa_dump.group(1))
                        if kappa_dump.group(3):
                            complex_expression = kappa_dump.group(3)
                        else:
                            complex_expression = kappa_dump.group(2)
                        building_complex = True

                    # Determine if this line is an entire complex (i.e. starts with an init and ends in a closing
                    # parenthesis)
                    elif re.search('^%init:\s\d+\s(/\*.+\*/)?.+\)$', line):
                        kappa_dump = re.search('^%init:\s(\d+)\s(/\*.+\*/)?(.+\))', line)
                        complex_abundance = int(kappa_dump.group(1))
                        if kappa_dump.group(3):
                            complex_expression = KappaComplex(kappa_dump.group(3))
                        else:
                            complex_expression = KappaComplex(kappa_dump.group(2))
                        self.snapshot[complex_expression] = complex_abundance

                    # Determine if this line is the time definition line, if so get snapshot's time
                    elif re.search('^%def:\s\"T0\"\s\"\d+\.?\d*\"', line):
                        tmp = re.search('%def:\s\"T0\"\s\"(\d+\.?\d*)\"', line)
                        self.snapshot_time = tmp.group(1)

                    # Determine if this is the even definition line, if so get snapshot's event number
                    elif re.search('^//\sSnapshot\s\[Event:\s\d+\]', line):
                        tmp = re.search('^//\sSnapshot\s\[Event:\s(\d+)\]', line)
                        self.snapshot_event = tmp.group(1)


    def get_snapshot_file_name(self):
        """Returns a string with the name of the file this snapshot came from."""
        return str(self.file_name)


    def get_snapshot_time(self):
        """Returns a float with the time at which this snapshot was taken."""
        return float(self.snapshot_time)

    def get_snapshot_event(self):
        """Returns an integer with the event number the snapshot was taken at."""
        return int(self.snapshot_event)

    def get_all_complexes(self):
        """Returns a list of KappaComplexes with all the complexes in the snapshot."""
        return list(self.snapshot.keys())

    def get_all_abundances(self):
        """Returns a list of integers with all the abundances in the snapshot."""
        return list(self.snapshot.values())

    def get_all_sizes(self):
        """Returns a list of integers with all the complex sizes visible in the snapshot, one item per complex (i.e. can
        contain repeat numbers if they correspond to different complexes)."""
        sizes = [c.get_size_of_complex() for c in self.get_all_complexes()]
        return sizes

    def get_agent_types_present(self):
        """Returns a set with the names of the agents present in the snapshot."""
        agent_types = set()
        for c in self.get_all_complexes():
            agent_types.update(c.get_agent_types())
        return agent_types

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

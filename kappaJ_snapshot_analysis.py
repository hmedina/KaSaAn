#! /usr/bin/python3
""" This is are the core functions and definitions used to analyze snapshots. The parser is compatible with Kappa syntax
 4, and is intended as the working & supported version. """

import json


class KappaSnapshot:
    """Class for representing Kappa snapshots. A snapshot is represented as a dictionary, where the kappa expression
    serves as the key, and the abundance serves as the value. Many of the methods for this class are simple re-namings
     of the Dict() class', but with more informative names for kappa entities."""

    def __init__(self, snapshot_file_name):
        with open(snapshot_file_name) as jf:
            read_file = json.load(jf)
        self.raw = read_file

    def get_snapshot_time(self):
        """Returns a float with the time at which this snapshot was taken."""
        return float(self.raw['snapshot_time'])

    def get_snapshot_event(self):
        """Returns an integer with the event number the snapshot was taken at."""
        return int(self.raw['snapshot_event'])

    def get_all_complexes(self):
        """Returns a list of KappaComplexes with all the complexes in the snapshot."""
        raise NotImplemented

    def get_all_abundances(self):
        """Returns a list of integers with all the abundances in the snapshot."""
        raise NotImplemented

    def get_all_complexes_and_abundances(self):
        """Returns a list of tuples, where the first element is a KappaComplex and the second is an int with the
        abundance of the corresponding complex."""
        raise NotImplemented

    def get_total_mass(self):
        """Returns an int with the total mass of the snapshot, measured in number of agents."""
        raise NotImplemented

    def get_complexes_with_abundance(self, query_abundance):
        """Returns a list of KappaComplexes present in the snapshot at the query abundance. For example, get all
        elements present in single copy."""
        raise NotImplemented

    def get_complexes_of_size(self, query_size):
        """Returns the list of complexes that are of the query size. For example, get all the dimers."""
        raise NotImplemented

    def get_largest_complexes(self):
        """Returns a list of KappaComplexes with the largest complexes, measured in number of constituting agents."""
        raise NotImplemented

    def get_smallest_complexes(self):
        """Returns a list of KappaComplexes with the smallest complexes, measured in number of constituting agents."""
        raise NotImplemented

    def get_most_abundant_complexes(self):
        """Returns the list of complexes found to be the most abundant. These could be the monomers for example."""
        raise NotImplemented

    def get_least_abundant_complexes(self):
        """Returns the list of complexes found to be the least abundant. For example, this would be the giant component,
        or the set of largest entities."""
        raise NotImplemented

    def get_size_distribution(self):
        """Returns a dictionary where the key is the size of a complex and the value is the amount of complexes with
        that size. For example, {1:3, 4:5} indicates the mixture contains only three monomers and five tetramers."""
        raise NotImplemented

    def plot_size_distribution(self):
        """"Plots the size distribution of complexes in the snapshot."""
        raise NotImplemented

    def plot_mass_distribution(self):
        """Plots the mass distribution of protomers in the snapshot: a monomer counts as one, a dimer as two, a trimer
        as three, and so on. Thus, five trimers have a mass of 15."""
        raise NotImplemented
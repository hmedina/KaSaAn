#! /usr/bin/python3

import re
from .KappaComplex import KappaComplex
from typing import List, Set, ItemsView, Dict


class KappaSnapshot:
    """Class for representing Kappa snapshots. A snapshot is represented as a dictionary, where the kappa expression
    serves as the key, and the abundance serves as the value. Many of the methods for this class are simple re-namings
     of the Dict() class', but with more informative names for kappa entities."""

    def __init__(self, snapshot_file_name: str):
        self.file_name = snapshot_file_name
        self.snapshot: Dict[KappaComplex, int] = dict()
        self.raw_view = str()

        # read file into a single string
        with open(snapshot_file_name, 'r') as kf:
            self.raw_view = kf.read()
        # remove newlines, split by "%init:" keyword
        digest: List[str] = self.raw_view.replace('\n', '').split('%init: ')

        # parse header and get event, uuid, time
        try:
            g = re.match('//\sSnapshot\s\[Event:\s(\d+)\]//\s\"uuid\"\s:\s\"(\w+)\"%def:\s\"T0\"\s\"([\d.]+)\"', digest[0])
            self.snapshot_event = int(g.group(1))
            self.snapshot_uuid = str(g.group(2))
            self.snapshot_time = float(g.group(3))
        except AttributeError:
            print('\nParsing error: Snapshot time, uuid, & T0 not found in <' + digest[0] + '>')
        # parse the complexes into instances of KappaComplexes, get their abundance, cross-check their size
        for entry in digest[1:]:
            try:
                g = re.match('^(\d+)\s/\*(\d+)\sagents\*/\s(.+)$', entry)
                abundance = int(g.group(1))
                size = int(g.group(2))
                species = KappaComplex(g.group(3))
                if not size == species.get_size_of_complex():
                    raise ValueError('Size mismatch: snapshot declares <' + str(size) +
                                     '>, I counted <' + str(species.get_size_of_complex()) + '>')
                # assign the complex as a key to the dictionary
                self.snapshot[species] = abundance
            except AttributeError:
                print('Parsing error: abundance, length, & complex not found at <' + entry + '>')

    def __repr__(self) -> str:
        return 'KappaSnapshot("{0}")'.format(self.file_name)

    def __str__(self) -> str:
        return self.raw_view

    def get_snapshot_file_name(self) -> str:
        """Returns a string with the name of the file this snapshot came from."""
        return self.file_name

    def get_snapshot_time(self) -> float:
        """Returns a float with the time at which this snapshot was taken."""
        return self.snapshot_time

    def get_snapshot_uuid(self) -> str:
        """Returns the UUID (Universally unique identifier) of the snapshot."""
        return self.snapshot_uuid

    def get_snapshot_event(self) -> int:
        """Returns an integer with the event number the snapshot was taken at."""
        return self.snapshot_event

    def get_all_complexes(self) -> List[KappaComplex]:
        """Returns a list of KappaComplexes with all the complexes in the snapshot."""
        return list(self.snapshot.keys())

    def get_all_abundances(self) -> List[int]:
        """Returns a list of integers with all the abundances in the snapshot."""
        return list(self.snapshot.values())

    def get_all_sizes(self) -> List[int]:
        """Returns a list of integers with all the complex sizes visible in the snapshot, one item per complex (i.e. can
        contain repeat numbers if they correspond to different complexes)."""
        sizes = [c.get_size_of_complex() for c in self.get_all_complexes()]
        return sizes

    def get_agent_types_present(self) -> Set[str]:
        """Returns a set with the names of the agents present in the snapshot."""
        agent_types = set()
        for c in self.get_all_complexes():
            agent_types.update(c.get_agent_types())
        return agent_types

    def get_all_complexes_and_abundances(self) -> ItemsView[KappaComplex, int]:
        """Returns a list of tuples, where the first element is a KappaComplex and the second is an int with the
        abundance of the corresponding complex."""
        return self.snapshot.items()

    def get_total_mass(self) -> int:
        """Returns an int with the total mass of the snapshot, measured in number of agents."""
        total_mass = 0
        for i_complex, i_abundance in self.get_all_complexes_and_abundances():
            total_mass += i_complex.get_size_of_complex() * i_abundance
        return total_mass

    def get_complexes_with_abundance(self, query_abundance: int) -> List[KappaComplex]:
        """Returns a list of KappaComplexes present in the snapshot at the query abundance. For example, get all
        elements present in single copy."""
        result_complexes = []
        for complex_expression, complex_abundance in self.get_all_complexes_and_abundances():
            if query_abundance == complex_abundance:
                result_complexes.append(complex_expression)
        return result_complexes

    def get_complexes_of_size(self, query_size: int) -> List[KappaComplex]:
        """Returns the list of complexes that are of the query size. For example, get all the dimers."""
        result_complexes = []
        for complex_expression in self.get_all_complexes():
            if query_size == complex_expression.get_size_of_complex():
                result_complexes.append(complex_expression)
        return result_complexes

    def get_largest_complexes(self) -> List[KappaComplex]:
        """Returns a list of KappaComplexes of the largest size, measured in number of constituting agents."""
        max_known_size = 0
        for complex_expression in self.get_all_complexes():
            current_size = complex_expression.get_size_of_complex()
            if current_size > max_known_size:
                max_known_size = current_size
        return self.get_complexes_of_size(max_known_size)

    def get_smallest_complexes(self) -> List[KappaComplex]:
        """Returns a list of KappaComplexes with the smallest complexes, measured in number of constituting agents."""
        min_known_size = self.get_largest_complexes()[0].get_size_of_complex() + 1
        for complex_expression in self.get_all_complexes():
            current_size = complex_expression.get_size_of_complex()
            if current_size < min_known_size:
                min_known_size = current_size
        return self.get_complexes_of_size(min_known_size)

    def get_most_abundant_complexes(self) -> List[KappaComplex]:
        """Returns the list of complexes found to be the most abundant. These could be the monomers for example."""
        max_abundance = max(self.get_all_abundances())
        return self.get_complexes_with_abundance(max_abundance)

    def get_least_abundant_complexes(self) -> List[KappaComplex]:
        """Returns the list of complexes found to be the least abundant. For example, this would be the giant component,
        or the set of largest entities."""
        min_abundance = min(self.get_all_abundances())
        return self.get_complexes_with_abundance(min_abundance)

    def get_size_distribution(self) -> Dict[int, int]:
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

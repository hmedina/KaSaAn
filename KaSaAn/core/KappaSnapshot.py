#!/usr/bin/env python3

import re
import os
import warnings
from typing import List, Set, ItemsView, Dict

from .KappaEntity import KappaEntity
from .KappaComplex import KappaComplex
from .KappaAgent import KappaAgent, KappaToken
from .KappaError import SnapshotAgentParseError, SnapshotTokenParseError, SnapshotParseError


class KappaSnapshot(KappaEntity):
    """Class for representing Kappa snapshots. A snapshot is represented as a dictionary, where the kappa expression
     serves as the key, and the abundance serves as the value. Many of the methods for this class are simple re-namings
     of the Dict() class', but with more informative names for Kappa entities."""

    def __init__(self, snapshot_file_name: str):
        self._file_name: str
        self._complexes: Dict[KappaComplex, int]
        self._tokens: Dict[str: KappaToken]
        self._raw_expression: str
        self._kappa_expression: str
        self._snapshot_event: int
        self._snapshot_uuid: str
        self._snapshot_time: float

        self._file_name = os.path.split(snapshot_file_name)[1]
        self._complexes = dict()
        self._tokens = dict()
        # read file into a single string
        with open(snapshot_file_name, 'r') as kf:
            self._raw_expression = kf.read()
        # remove newlines, split by "%init:" keyword
        digest: List[str] = self._raw_expression.replace('\n', '').split('%init: ')
        # parse header and get event, uuid, time
        g = re.match('//\sSnapshot\s\[Event:\s(\d+)\]//\s\"uuid\"\s:\s\"(\w+)\"%def:\s\"T0\"\s\"([0-9]+|([0-9]+[eE][+-]?[0-9+])|((([0-9]+\.[0-9]*)|(\.[0-9]+))([eE][+-]?[0-9]+)?))\"', digest[0])
        if not g:
            raise SnapshotParseError('Snapshot header <' + digest[0] + '> could not be parsed in <' + snapshot_file_name + '>')
        self._snapshot_event = int(g.group(1))
        self._snapshot_uuid = str(g.group(2))
        self._snapshot_time = float(g.group(3))
        # parse the complexes into instances of KappaComplexes, get their abundance, cross-check their size
        for entry in digest[1:]:
            try:
                try:
                    # try to parse as a KappaComplex line, with agents
                    g = re.match('^(\d+)\s/\*(\d+)\sagents\*/\s(.+)$', entry)
                    if not g:
                        raise SnapshotAgentParseError('Abundance, length, & complex not found in <' + entry + '> in <' + snapshot_file_name + '>')
                    abundance = int(g.group(1))
                    size = int(g.group(2))
                    species = KappaComplex(g.group(3))
                    if not size == species.get_size_of_complex():
                        raise ValueError('Size mismatch: snapshot declares <' + str(size) +
                                         '>, I counted <' + str(species.get_size_of_complex()) + '> in <' + snapshot_file_name + '>')
                    # assign the complex as a key to the dictionary
                    self._complexes[species] = abundance
                except SnapshotAgentParseError:
                    # try to parse as a token line instead
                    tk_value_pat = '((?:(?:\d+\.\d+)|(?:\d+\.)|(?:\.\d+)|(?:\d+))[eE]?[+-]?\d?)'
                    tk_name_pat = '([_~][a-zA-Z0-9_~+-]+|[a-zA-Z][a-zA-Z0-9_~+-]*)'
                    tk_pat = '^' + tk_value_pat + '\s' + tk_name_pat + '$'
                    g = re.match(tk_pat, entry)
                    if not g:
                        raise SnapshotTokenParseError('Abundance & token name not found in <' + entry + '> in <' + snapshot_file_name + '>')
                    # assign the token as a key to the dictionary
                    tk = KappaToken(g.group(0))
                    self._tokens[tk.get_token_name()] = tk
            except SnapshotTokenParseError:
                raise SnapshotParseError('Could not parse as either complex line nor token line <' + entry + '> in <' + snapshot_file_name + '>')
        # canonicalize the kappa expression: tokens
        self._kappa_expression = '\n'.join(['%init: ' + str(float(tk.get_token_operation())) + ' ' + tk.get_token_name()
                                            for tk in self._tokens.values()])
        self._kappa_expression += '\n' if self._tokens else ''
        # canonicalize the kappa expression: complexes
        self._kappa_expression += '\n'.join(['%init: ' + str(self._complexes[cx]) + ' ' + str(cx)
                                            for cx in self._complexes.keys()])

    def get_snapshot_file_name(self) -> str:
        """Returns a string with the name of the file this snapshot came from."""
        return self._file_name

    def get_snapshot_time(self) -> float:
        """Returns a float with the time at which this snapshot was taken."""
        return self._snapshot_time

    def get_snapshot_uuid(self) -> str:
        """Returns the UUID (Universally unique identifier) of the snapshot."""
        return self._snapshot_uuid

    def get_snapshot_event(self) -> int:
        """Returns an integer with the event number the snapshot was taken at."""
        return self._snapshot_event

    def get_all_complexes(self) -> List[KappaComplex]:
        """Returns a list of KappaComplexes with all the complexes in the snapshot."""
        return list(self._complexes.keys())

    def get_all_abundances(self) -> List[int]:
        """Returns a list of integers with all the abundances in the snapshot."""
        return list(self._complexes.values())

    def get_all_sizes(self) -> List[int]:
        """Returns a list of integers with all the complex sizes visible in the snapshot, one item per complex (i.e. can
        contain repeat numbers if they correspond to different complexes)."""
        sizes = [key.get_size_of_complex() for key in self._complexes.keys()]
        return sizes

    def get_agent_types_present(self) -> Set[KappaAgent]:
        """Returns a set with the names of the agents present in the snapshot."""
        agent_types = set()
        for key in self._complexes.keys():
            agent_types.update(key.get_agent_types())
        return agent_types

    def get_all_complexes_and_abundances(self) -> ItemsView[KappaComplex, int]:
        """Returns a list of tuples, where the first element is a KappaComplex and the second is an int with the
        abundance of the corresponding complex."""
        return self._complexes.items()

    def get_total_mass(self) -> int:
        """Returns an int with the total mass of the snapshot, measured in number of agents."""
        total_mass = 0
        for i_complex, i_abundance in self._complexes.items():
            total_mass += i_complex.get_size_of_complex() * i_abundance
        return total_mass

    def get_abundance_of_agent(self, query_agent) -> int:
        """Returns an int with the abundance of the given agent. Supports passing a string with the agent expression, or
        and instance of a KappaAgent. Supports passing agents with signature, e.g. Bob(site{state})."""
        if type(query_agent) is not KappaAgent:
            query_agent = KappaAgent(query_agent)
        abundance = 0
        for cx, cx_ab in self.get_all_complexes_and_abundances():
            intra_cx_ab = cx.get_number_of_embeddings_of_agent(query_agent)
            abundance += intra_cx_ab * cx_ab
        return abundance

    def get_complexes_with_abundance(self, query_abundance: int) -> List[KappaComplex]:
        """Returns a list of KappaComplexes present in the snapshot at the query abundance. For example, get all
        elements present in single copy."""
        result_complexes = []
        for complex_expression, complex_abundance in self._complexes.items():
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

    def get_all_tokens_and_values(self) -> Dict[str, float]:
        """Returns a dictionary with the tokens present in the snapshot in the form of [name]:[value]."""
        d = dict()
        for item in self._tokens.values():
            d[item.get_token_name()] = float(item.get_token_operation())
        return d

    def get_value_of_token(self, query) -> float:
        """Returns the value of a token."""
        # make it a KappaToken, if it's not one already
        if not type(query) is KappaToken:
            q = KappaToken(query)
        else:
            q = query
        # return value, if token is present
        if q.get_token_name() in self._tokens:
            value = float(self._tokens[q].get_token_operation())
        else:
            warnings.warn('Token <' + str(query) + '> not found in this snapshot.')
            value = None
        return value


    def get_token_names(self) -> List[str]:
        """Returns the token names present in the snapshot."""
        return list(self._tokens.keys())
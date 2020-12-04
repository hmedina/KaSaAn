#!/usr/bin/env python3

import re
import os
import warnings
import networkx as nx
from typing import List, Set, ItemsView, Dict, Tuple

from .KappaEntity import KappaEntity
from .KappaComplex import KappaComplex
from .KappaAgent import KappaAgent, KappaToken
from .KappaError import SnapshotAgentParseError, SnapshotTokenParseError, SnapshotParseError


class KappaSnapshot(KappaEntity):
    """Class for representing Kappa snapshots. A snapshot is represented as a dictionary, where the kappa expression
     serves as the key, and the abundance serves as the value. Many of the methods for this class are simple re-namings
     of the Dict() class', but with more informative names for Kappa entities."""

    def __init__(self, snapshot_file_name: str):
        # type declarations
        self._file_name: str
        self._complexes: Dict[KappaComplex, int]
        self._tokens: Dict[str: KappaToken]
        self._known_sizes: List[int]
        self._identifier_complex_map: Dict[int, KappaComplex]
        self._raw_expression: str
        self._kappa_expression: str
        self._snapshot_event: int
        self._snapshot_uuid: str
        self._snapshot_time: float
        # initialization of structures
        self._file_name = os.path.split(snapshot_file_name)[1]
        self._complexes = dict()
        self._tokens = dict()
        self._known_sizes = []
        self._identifier_complex_map = {}
        # read file into a single string
        with open(snapshot_file_name, 'r') as kf:
            self._raw_expression = kf.read()
        # remove newlines, split by "%init:" keyword
        digest: List[str] = self._raw_expression.replace('\n', '').split('%init: ')
        # parse header and get event, uuid, time
        g = re.match(
            r'//\sSnapshot\s' +
            r'\[Event:\s(\d+)\]//\s' +
            r'\"uuid\"\s:\s\"(\w+)' +
            r'\"%def:\s\"T0\"\s\"([0-9]+|([0-9]+[eE][+-]?[0-9+])|((([0-9]+\.[0-9]*)|(\.[0-9]+))([eE][+-]?[0-9]+)?))\"',
            digest[0])
        if not g:
            raise SnapshotParseError('Header <' + digest[0] + '> not be parsed in <' + snapshot_file_name + '>')
        self._snapshot_event = int(g.group(1))
        self._snapshot_uuid = str(g.group(2))
        self._snapshot_time = float(g.group(3))
        # parse the complexes into instances of KappaComplexes, get their abundance, cross-check their size
        for entry in digest[1:]:
            try:
                try:
                    # try to parse as a KappaComplex line, with agents
                    g = re.match(r'^(\d+)\s/\*(\d+)\sagents\*/\s(.+)$', entry)
                    if not g:
                        raise SnapshotAgentParseError(
                            'Abundance, length, & complex not found in <' + entry + '> in <' + snapshot_file_name + '>')
                    abundance = int(g.group(1))
                    size = int(g.group(2))
                    species = KappaComplex(g.group(3))
                    if not size == species.get_size_of_complex():
                        raise ValueError(
                            'Size mismatch: snapshot declares <' + str(size) + '>, I counted <' +
                            str(species.get_size_of_complex()) + '> in <' + snapshot_file_name + '>')
                    # assign the complex as a key to the dictionary
                    self._complexes[species] = abundance
                    self._known_sizes.append(size)
                    # define identifier -> complex map
                    if species.get_agent_identifiers():
                        for identifier in species.get_agent_identifiers():
                            self._identifier_complex_map[identifier] = species
                except SnapshotAgentParseError:
                    # try to parse as a token line instead
                    tk_value_pat = r'((?:(?:\d+\.\d+)|(?:\d+\.)|(?:\.\d+)|(?:\d+))[eE]?[+-]?\d?)'
                    tk_name_pat = r'([_~][a-zA-Z0-9_~+-]+|[a-zA-Z][a-zA-Z0-9_~+-]*)'
                    tk_pat = r'^' + tk_value_pat + r'\s' + tk_name_pat + r'$'
                    g = re.match(tk_pat, entry)
                    if not g:
                        raise SnapshotTokenParseError(
                            'Abundance & token name not found in <' + entry + '> in <' + snapshot_file_name + '>')
                    # assign the token as a key to the dictionary
                    tk = KappaToken(g.group(0))
                    self._tokens[tk.get_token_name()] = tk
            except SnapshotTokenParseError:
                raise SnapshotParseError(
                    'Complex and token parse failed for <' + entry + '> in <' + snapshot_file_name + '>')
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

    def get_composition(self) -> Dict[KappaAgent, int]:
        """Return a dictionary where the keys are KappaAgents, their names, and their value is the abundance in the
        snapshot of those agents."""
        agent_types = self.get_agent_types_present()
        composition = dict(zip(agent_types, [0] * len(agent_types)))
        for agent_type in agent_types:
            for kappa_complex, abundance in self.get_all_complexes_and_abundances():
                complex_composition = kappa_complex.get_complex_composition()
                local_abundance = complex_composition[agent_type] if agent_type in complex_composition else 0
                composition[agent_type] += abundance * local_abundance
        return composition

    def get_complexes_with_abundance(self, query_abundance: int) -> List[KappaComplex]:
        """Returns a list of KappaComplexes present in the snapshot at the query abundance. For example, get all
        elements present in single copy."""
        result_complexes = []
        for complex_expression, complex_abundance in self._complexes.items():
            if query_abundance == complex_abundance:
                result_complexes.append(complex_expression)
        return result_complexes

    def get_complexes_of_size(self, query_size: int) -> List[Tuple[KappaComplex, int]]:
        """Returns the list tuples, with complexes and their abudnace, for complexes that are of the query size. For
        example, get all the dimers and their respective abundances."""
        result_complexes = []
        for comp, abun in self.get_all_complexes_and_abundances():
            if query_size == comp.get_size_of_complex():
                result_complexes.append((comp, abun))
        return result_complexes

    def get_largest_complexes(self) -> List[Tuple[KappaComplex, int]]:
        """Returns a list of KappaComplexes of the largest size, measured in number of constituting agents."""
        max_known_size = max(self._known_sizes)
        return self.get_complexes_of_size(max_known_size)

    def get_smallest_complexes(self) -> List[Tuple[KappaComplex, int]]:
        """Returns a list of KappaComplexes with the smallest complexes, measured in number of constituting agents."""
        min_known_size = min(self._known_sizes)
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
        that size. For example, {1:3, 4:5} indicates the mixture contains only three monomers and five tetramers.
        Dictionary is sorted by increasing complex size."""
        size_dist = dict()
        for complex_expression, complex_abundance in self.get_all_complexes_and_abundances():
            current_size = complex_expression.get_size_of_complex()
            if current_size in size_dist:
                size_dist[current_size] += complex_abundance
            else:
                size_dist[current_size] = complex_abundance
        sorted_dist = dict(sorted(size_dist.items(), key=lambda item: item[0]))
        return sorted_dist

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

    def get_agent_identifiers(self) -> List[int]:
        """Returns a list with all the agent identifiers held in the snapshot."""
        return list(self._identifier_complex_map.keys())

    def get_complex_of_agent(self, query_identifier: int) -> KappaComplex:
        """Returns the KappaComplex containing the supplied agent identifier. Abundances are not returned as they
        should always be numerically 1; the identifier print-out forces distinction of species that would otherwise
        be identical, and identifiers are unique and stable throughout the simulation."""
        if self._identifier_complex_map:
            try:
                return self._identifier_complex_map[query_identifier]
            except KeyError as e:
                raise ValueError('Identifier <{}> not present in snapshot <{}>.'.format(
                    query_identifier, self.get_snapshot_file_name())) from e
        else:
            raise ValueError('Snapshot <{}> was not found to contain agent identifiers (i.e. raw formatted).'.format(
                self.get_snapshot_file_name()))

    def to_networkx(self) -> nx.MultiGraph:
        """Returns a Multigraph representation of the snapshot, abstracting away binding site data. Nodes represent
        agents, edges their bonds. Nodes have an attribute dictionary where the key 'kappa' holds the KappaAgent.
        Edges have an attribute dictionary where the key 'bond id' holds the bond identifier from the Kappa expression.
        Node identifiers are integers, using the order of agent declaration. For a graph g, g.nodes.data() displays the
        node identifiers and their corresponding KappaAgents, and g.edges.data() displays the edges, using the node
        identifiers as well as the kappa identifiers."""
        agent_node_id = 0
        snapshot_network = nx.MultiGraph()
        # iterate over all molecular species
        # then iterate over the number of times that species appears in the mix
        for molecular_species, species_abundance in self.get_all_complexes_and_abundances():
            for species_copy in range(species_abundance):
                # reconstruct the species, assign identifiers
                dangle_bond_list = {}  # store unpaired bonds here
                paired_bond_list = []  # store tuples of (agent index 1, agent index 2, bond identifier)
                for agent in molecular_species.get_all_agents():
                    snapshot_network.add_node(agent_node_id, kappa=agent)
                    for bond in agent.get_bond_identifiers():
                        if bond in dangle_bond_list:
                            paired_bond_list.append((dangle_bond_list[bond], agent_node_id, {'bond id': bond}))
                            del dangle_bond_list[bond]
                        else:
                            dangle_bond_list[bond] = agent_node_id
                    agent_node_id += 1
                if dangle_bond_list:
                    raise ValueError('Dangling bonds <' + ','.join(dangle_bond_list.keys()) +
                                     '> found in: ' + self._raw_expression)
                snapshot_network.add_edges_from(paired_bond_list)
        if snapshot_network.number_of_nodes() != self.get_total_mass():
            raise SnapshotParseError('Mismatch between snapshot mass <' + str(self.get_total_mass()) +
                                     '> and number of nodes in network <' + str(snapshot_network.number_of_nodes()) +
                                     '> for snapshot <' + self.get_snapshot_file_name() + '>')
        return snapshot_network

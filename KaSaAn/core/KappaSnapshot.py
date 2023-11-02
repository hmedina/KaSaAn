#!/usr/bin/env python3
"""Contains the `KappaSnapshot` class, meant to represent a fully specified state of a reaction mixture."""

import concurrent.futures as cofu
import re
import os
import warnings
import networkx as nx
import numpy as np
import pathlib
import xml.etree.ElementTree as ET
from typing import List, Optional, Set, ItemsView, Dict, Tuple, Union

from .KappaMultiAgentGraph import KappaMultiAgentGraph
from .KappaComplex import KappaComplex, embed_and_map
from .KappaAgent import KappaAgent, KappaToken
from .KappaError import (
    SnapshotAgentParseError, SnapshotTokenParseError, SnapshotParseError, AgentParseError,
    ComplexParseError)


class KappaSnapshot(KappaMultiAgentGraph):
    """Class for representing Kappa snapshots. A snapshot contains a dictionary, where the kappa expression
     serves as the key, and the abundance serves as the value. Many of the methods for this class are simple re-namings
     of the `Dict()` class', but with more informative names for Kappa entities."""

    # define pattern for the header
    _header_title_pat = r"//\sSnapshot\s\[Event:\s(\d+)\]"
    _header_uuid_pat = r"//\s\"uuid\"\s:\s\"(\w+)\""
    _header_t_zero_pat = r"%def:\s\"T0\"\s\"" + \
                         r"([0-9]+|([0-9]+[eE][+-]?[0-9+])|((([0-9]+\.[0-9]*)|(\.[0-9]+))([eE][+-]?[0-9]+)?))\""
    _header_pat_re = re.compile(_header_title_pat + _header_uuid_pat + _header_t_zero_pat)
    _header_pat_vr = re.compile(_header_title_pat + _header_t_zero_pat)
    # define pattern for a KappaComplex entry line
    _line_complex_re = re.compile(r'^(\d+)\s/\*(\d+)\sagents\*/\s(.+)$')
    # define pattern for a KappaToken entry line
    _token_value_pat = r'((?:(?:\d+\.\d+)|(?:\d+\.)|(?:\.\d+)|(?:\d+))[eE]?[+-]?\d?)'
    _token_name_pat = r'([_~][a-zA-Z0-9_~+-]+|[a-zA-Z][a-zA-Z0-9_~+-]*)'
    _line_token_pat = r'^' + _token_value_pat + r'\s' + _token_name_pat + r'$'
    _line_token_re = re.compile(_line_token_pat)

    def __init__(self, snapshot_file: Union[pathlib.Path, str]):
        # type declarations
        self._file_name: str
        self._complexes: Dict[KappaComplex, int]
        self._tokens: Dict[str, KappaToken]
        self._known_sizes: List[int]
        self._identifier_complex_map: Dict[int, KappaComplex]
        self._raw_expression: str
        self._kappa_expression: str
        self._snapshot_event: int
        self._snapshot_uuid: str
        self._snapshot_time: float
        # initialization of structures
        if type(snapshot_file) == str:
            self._file_name = os.path.split(snapshot_file)[1]
        elif type(snapshot_file) == pathlib.PosixPath or type(snapshot_file) == pathlib.WindowsPath:
            self._file_name = str(snapshot_file)
        else:
            raise ValueError(
                'Snapshot initializer expected either a file name or a path-like object, got {}'.format(
                    type(snapshot_file)))
        self._complexes = dict()
        self._tokens = dict()
        self._known_sizes = []
        self._identifier_complex_map = {}
        # read file into a single string
        with open(snapshot_file, 'r') as kf:
            self._raw_expression = kf.read()
        # remove newlines, split by "%init:" keyword
        digest: List[str] = self._raw_expression.replace('\n', '').split('%init: ')
        # parse header and get event, uuid, time
        g = self._header_pat_re.match(digest[0])
        if g:
            self._snapshot_event = int(g.group(1))
            self._snapshot_uuid = str(g.group(2))
            self._snapshot_time = float(g.group(3))
        if not g:
            g = self._header_pat_vr.match(digest[0])
            if g:
                self._snapshot_event = int(g.group(1))
                self._snapshot_uuid = ''
                self._snapshot_time = float(g.group(2))
            if not g:
                raise SnapshotParseError('File {} contains unparseable header:\n{}'.format(self._file_name, digest[0]))

        # parse the complexes into instances of KappaComplexes, get their abundance, cross-check their size
        for entry in digest[1:]:
            try:
                try:
                    # try to parse as a KappaComplex line, with agents
                    g = self._line_complex_re.match(entry)
                    if not g:
                        raise SnapshotAgentParseError(
                            'Abundance, length, & complex not found in file {}, line said:\n{}'.format(
                                self._file_name, entry))
                    abundance = int(g.group(1))
                    size = int(g.group(2))
                    species = KappaComplex(g.group(3))
                    if not size == species.get_size_of_complex():
                        raise ValueError(
                            'Size mismatch: snapshot {} declares {}, I counted {} for species {}'.format(
                                self._file_name, size, species.get_size_of_complex(), species))
                    # assign the complex as a key to the dictionary
                    self._complexes[species] = abundance
                    self._known_sizes.append(size)
                    # define identifier -> complex map
                    for identifier in species.get_agent_identifiers():
                        self._identifier_complex_map[identifier] = species
                except SnapshotAgentParseError:
                    # try to parse as a token line instead
                    g = self._line_token_re.match(entry)
                    if not g:
                        raise SnapshotTokenParseError(
                            'Abundance & token name not found in file {}, line said:\n{}'.format(
                                self._file_name, entry))
                    # assign the token as a key to the dictionary
                    tk = KappaToken(g.group(0))
                    self._tokens[tk.get_token_name()] = tk
            except SnapshotTokenParseError:
                raise SnapshotParseError(
                    'Complex and token parse failed in file {}, line said:\n{}'.format(
                        self._file_name, entry))
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
        """Returns the UUID (universally unique identifier) of the snapshot."""
        return self._snapshot_uuid

    def get_snapshot_event(self) -> int:
        """Returns an integer with the event number the snapshot was taken at."""
        return self._snapshot_event

    def get_all_complexes(self) -> List[KappaComplex]:
        """Returns a list of `KappaComplexes` with all the complexes in the snapshot."""
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
        """Returns a set with the types of agents present in the snapshot."""
        agent_types = set()
        for key in self._complexes.keys():
            agent_types.update(key.get_agent_types())
        return agent_types

    def get_all_complexes_and_abundances(self) -> ItemsView[KappaComplex, int]:
        """Returns an iterable of tuples, where the first element is a `KappaComplex` and the second is an int with the
        abundance of the corresponding complex."""
        return self._complexes.items()

    def get_total_mass(self) -> int:
        """Returns an integer with the total mass of the snapshot, measured in number of agents."""
        total_mass = 0
        for i_complex, i_abundance in self._complexes.items():
            total_mass += i_complex.get_size_of_complex() * i_abundance
        return total_mass

    def get_abundance_of_agent(self, query_agent) -> int:
        """Returns an integer with the abundance of the given agent. Supports passing a string with the agent
        expression, or an instance of a KappaAgent. Supports passing agents with signature, e.g. `Bob(site{state})`."""
        if type(query_agent) is not KappaAgent:
            query_agent = KappaAgent(query_agent)
        abundance = 0
        for cx, cx_ab in self.get_all_complexes_and_abundances():
            intra_cx_ab = cx.get_number_of_embeddings_of_agent(query_agent)
            abundance += intra_cx_ab * cx_ab
        return abundance

    def get_abundance_of_pattern(self, query_pattern, multi_thread: bool = False) -> Tuple[int, int]:
        """
Returns the number of times the pattern appears in the query, both the raw embedding number as well as
the symmetry-corrected one. For single-agent patterns, there are no symmetry corrections needed, so the same
value is returned twice.

Optional parameter to use a multi-process pool of workers for embedding the pattern on the various
complexes in the mixture, false by default. My intuition told me it would be faster to check multiple complexes
at a time; however my regular usage shows marginal gains in some cases, negligible ones often, and frequently
markedly slower performance with multi-threading than without. Case-specific, your milage may vary.
        """
        # if given string, attempt to cast
        if type(query_pattern) is str:
            try:
                try:
                    query_pattern = KappaAgent(query_pattern)
                except AgentParseError:
                    query_pattern = KappaComplex(query_pattern)
            except ComplexParseError:
                raise ValueError('Could not parse input <{}> as KappaAgent nor KappaComplex'.format(query_pattern))
        # once cast, proceed
        if type(query_pattern) is KappaAgent:
            return tuple([self.get_abundance_of_agent(query_pattern)] * 2)
        elif type(query_pattern) is KappaComplex:
            abundances_all = np.zeros(len(self.get_all_complexes()))
            abundances_unique = np.zeros(len(self.get_all_complexes()))
            if not multi_thread:
                for ka_index, ka_details in enumerate(self.get_all_complexes_and_abundances()):
                    map_all, map_unique = embed_and_map(query_pattern, ka_details[0])
                    abundances_all[ka_index] += len(map_all) * ka_details[1]
                    abundances_unique[ka_index] += len(map_unique) * ka_details[1]
            else:
                map_inputs = zip([query_pattern] * len(self.get_all_complexes()), self.get_all_complexes())
                maps_all = []
                maps_unique = []
                with cofu.ThreadPoolExecutor() as executor:
                    jobs_submitted = {executor.submit(embed_and_map, *map_input): map_input for map_input in map_inputs}
                    for job in cofu.as_completed(jobs_submitted):
                        input_used = jobs_submitted[job]
                        try:
                            data = job.result()
                        except Exception as exc:
                            print('{} generated an exception: {}'.format(input_used, exc))
                        else:
                            maps_all.append(data[0])
                            maps_unique.append(data[1])
                abundances_all = [len(item) for item in maps_all]
                abundances_unique = [len(item) for item in maps_unique]
                abundances_all *= np.array(self.get_all_abundances())
                abundances_unique *= np.array(self.get_all_abundances())
            return np.sum(abundances_all, dtype=int), np.sum(abundances_unique, dtype=int)
        else:
            raise ValueError('Expected string, KappaAgent, or KappaComplex, got {}'.format(type(query_pattern)))

    def get_composition(self) -> Dict[KappaAgent, int]:
        """Return a dictionary where the keys are `KappaAgents`, the types and their abundance in the snapshot. This is
        akin to the sum formula of the snapshot."""
        agent_types = self.get_agent_types_present()
        composition = dict(zip(agent_types, [0] * len(agent_types)))
        for agent_type in agent_types:
            for kappa_complex, abundance in self.get_all_complexes_and_abundances():
                complex_composition = kappa_complex.get_complex_composition()
                local_abundance = complex_composition[agent_type] if agent_type in complex_composition else 0
                composition[agent_type] += abundance * local_abundance
        return composition

    def get_complexes_with_abundance(self, query_abundance: int) -> List[KappaComplex]:
        """Returns a list of `KappaComplexes` present in the snapshot at the queried abundance. For example, get all
        elements present in single copy."""
        result_complexes = []
        for complex_expression, complex_abundance in self._complexes.items():
            if query_abundance == complex_abundance:
                result_complexes.append(complex_expression)
        return result_complexes

    def get_complexes_of_size(self, query_size: int) -> List[Tuple[KappaComplex, int]]:
        """Returns a list tuples, with complexes and their abundance, for complexes that are of the query size. For
        example, get all the dimers and their respective abundances."""
        result_complexes = []
        for comp, abun in self.get_all_complexes_and_abundances():
            if query_size == comp.get_size_of_complex():
                result_complexes.append((comp, abun))
        return result_complexes

    def get_largest_complexes(self) -> List[Tuple[KappaComplex, int]]:
        """Returns a list of KappaComplexes of the largest size, measured in number of constituting agents, along with
        their abundance in the snapshot."""
        max_known_size = max(self._known_sizes)
        return self.get_complexes_of_size(max_known_size)

    def get_smallest_complexes(self) -> List[Tuple[KappaComplex, int]]:
        """Returns a list of KappaComplexes with the smallest complexes, measured in number of constituting agents,
        along with their abundance in the snapshot."""
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
        that size. For example, `{1:3, 4:5}` indicates the mixture contains only three monomers and five tetramers.
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
        """Returns a dictionary with the tokens present in the snapshot in the form of `[name]:[value]`."""
        d = dict()
        for item in self._tokens.values():
            d[item.get_token_name()] = float(item.get_token_operation())
        return d

    def get_value_of_token(self, query) -> Union[None, float]:
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

    def get_complex_of_agent(self, query_identifier: int) -> Union[KappaComplex, None]:
        """Returns the KappaComplex containing the supplied agent identifier. Abundances are not returned as they
        should always be numerically 1: the identifier print-out forces distinction of species that would otherwise
        be identical, and identifiers are unique and stable throughout the simulation."""
        if query_identifier in self._identifier_complex_map:
            return self._identifier_complex_map[query_identifier]
        else:
            Warning('Returnin None; identifier {} not present in snapshot {}'.format(
                query_identifier, self.get_snapshot_file_name()))
            return None

    def get_agent_from_identifier(self, ident: int) -> Union[KappaAgent, None]:
        """Returns the KappaAgent associated with the given identifier, if any."""
        if ident in self._identifier_complex_map:
            return self.get_complex_of_agent(ident).get_agent_from_identifier(ident)
        else:
            Warning('Returnin None; identifier {} not present in snapshot {}'.format(
                ident, self.get_snapshot_file_name()))
            return None

    def to_networkx(self) -> nx.MultiGraph:
        """Returns a Multigraph representation of the snapshot, abstracting away binding site data. Nodes represent
        agents, edges their bonds. Nodes have an attribute dictionary where the key 'kappa' holds the KappaAgent.
        Edges have an attribute dictionary where the key 'bond id' holds the bond identifier from the Kappa expression.
        Node identifiers are integers, using the order of agent declaration. For a graph g, g.nodes.data() displays the
        node identifiers and their corresponding KappaAgents, and g.edges.data() displays the edges, using the node
        identifiers as well as the kappa identifiers."""
        agent_id_counter = 0
        snapshot_network = nx.MultiGraph()
        # iterate over all molecular species
        # then iterate over the number of times that species appears in the mix
        for molecular_species, species_abundance in self.get_all_complexes_and_abundances():
            for _ in range(species_abundance):
                species_network = molecular_species.to_networkx(identifier_offset=agent_id_counter)
                snapshot_network.update(species_network)
                # if we are not dealing with labeled agents, increase offset once per network added
                if not self.get_agent_identifiers():
                    agent_id_counter += molecular_species.get_size_of_complex()
        if snapshot_network.number_of_nodes() != self.get_total_mass():
            raise SnapshotParseError('Mismatch between snapshot mass <' + str(self.get_total_mass()) +
                                     '> and number of nodes in network <' + str(snapshot_network.number_of_nodes()) +
                                     '> for snapshot <' + self.get_snapshot_file_name() + '>')
        return snapshot_network

    def to_cytoscape_cx(self) -> List[Dict]:
        """Export to a structure that via some json encoding and dumping can be read by Cytoscape as a CX file. Usage:
        >>> import json
        >>> from KaSaAn.core import KappaSnapshot
        >>> my_snap = KappaSnapshot('some_snap.ka')
        >>> my_cx = my_snap.to_cytoscape_cx()
        >>> with open('my_cx.cx', 'w') as out_file:
        >>>    json.dump(my_cx, out_file)
        """
        cx_data = self._kappa_to_cytoscape_cx()
        cx_network_attributes = [{'n': 'name', 'v': self.get_snapshot_file_name()},
                                 {'n': 'time', 'v': self.get_snapshot_time()},
                                 {'n': 'event', 'v': self.get_snapshot_event()},
                                 {'n': 'UUID', 'v': self.get_snapshot_uuid()}]
        cx_data.insert(2, {'networkAttributes': cx_network_attributes})
        return cx_data

    def to_graphml(self, outfile: Union[pathlib.Path, str, None], node_coloring: Optional[Dict[KappaAgent, any]]) -> ET.ElementTree:
        """Returns an XML ElementTree with a GraphML representation of the snapshot, using GraphML's ports for
         binding sites. If an output file is given, object is indented & serialized to that file.
         Optional argument `node_coloring` colorizes by single-agent patterns."""
        this_tree = self._kappa_to_graphml(node_coloring)
        if outfile is not None:
            ET.indent(this_tree, space='\t')
            this_tree.write(outfile, encoding='UTF-8', xml_declaration=True, method='xml')
        return this_tree

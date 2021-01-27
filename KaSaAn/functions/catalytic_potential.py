#!/usr/bin/env python3

import glob
import warnings
from typing import List

from ..core import KappaSnapshot, KappaAgent
from .numerical_sort import numerical_sort


def get_potential_of_snapshot(snapshot, enzyme, substrate) -> int:
    """"The catalytic potential of a snapshot is a number. Each molecular species will contain a (possibly zero)
    quantity of enzymes, and another of substrates. Their product is the catalytic potential of the species. The sum
    over the species in a snapshot yields the catalytic potential of the snapshot."""
    # If not already KappaEntities, try to convert them into ones, i.e. from strings for expressions or filenames
    if not type(enzyme) is KappaAgent:
        enzyme = KappaAgent(enzyme)
    if not type(substrate) is KappaAgent:
        substrate = KappaAgent(substrate)
    if not type(snapshot) is KappaSnapshot:
        snapshot = KappaSnapshot(snapshot)
    # Sanity check: both requested agent names are present in the snapshot
    if enzyme not in snapshot.get_agent_types_present():
        warnings.warn(
            'Agent name <' + enzyme.get_agent_name() + '> + not in <' + snapshot.get_snapshot_file_name() + '>')
    if substrate not in snapshot.get_agent_types_present():
        warnings.warn(
            'Agent name <' + substrate.get_agent_name() + '> + not in <' + snapshot.get_snapshot_file_name() + '>')
    # Iterate over each complex and calculate its catalytic potential, q
    cat_pot = 0
    for mol_spec, ab in snapshot.get_all_complexes_and_abundances():
        e = mol_spec.get_number_of_embeddings_of_agent(enzyme)
        s = mol_spec.get_number_of_embeddings_of_agent(substrate)
        cat_pot += e * s * ab
    return cat_pot


def get_potential_of_folder(base_directory: str, enzyme: KappaAgent, substrate: KappaAgent,
                            verbosity: bool, snap_name_prefix: str) -> List[int]:
    if base_directory[-1] != '/':
        base_directory += '/'
    # Get the file names of snapshots in specified directory
    snap_names = sorted(glob.glob(base_directory + snap_name_prefix + '*.ka'), key=numerical_sort)
    snap_num = len(snap_names)
    if verbosity:
        print('Found ' + str(snap_num) + ' snapshots in directory ' + base_directory)
    if snap_num < 2:
        warnings.warn('Found less than two snapshots.')
    # Iterate over the files and calculate each's catalytic potential
    cat_pot_dist = []
    snap_num = len(snap_names)
    for snap_index in range(snap_num):
        snap_name = snap_names[snap_index]
        if verbosity:
            print('Now parsing file <{}>, {} of {}, {}%'.format(
                snap_name, snap_index, snap_num, 100*snap_index/snap_num))
        cat_pot_dist.append(get_potential_of_snapshot(snap_name, enzyme, substrate))
    return cat_pot_dist

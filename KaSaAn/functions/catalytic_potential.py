#!/usr/bin/env python3

import warnings
from typing import List, Tuple
from ..core import KappaSnapshot, KappaAgent
from .find_snapshot_names import find_snapshot_names


def _get_potential_of_snapshot(snapshot, enzyme, substrate) -> int:
    """The catalytic potential of a snapshot is a number. Each molecular species will contain a (possibly zero)
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
                            verbosity: bool, snap_name_pattern: str) -> List[Tuple[int, float]]:
    """See file under `KaSaAn.scripts` for usage."""
    # Get the file names of snapshots in specified directory
    snap_names = find_snapshot_names(base_directory, name_pattern=snap_name_pattern)
    snap_num = len(snap_names)
    if verbosity:
        print('Found {} snapshots in {}'.format(snap_num, base_directory))
    if snap_num < 2:
        warnings.warn('Found less than two snapshots.')
    # Iterate over the files and calculate each's catalytic potential
    cat_pot_dist = []
    for snap_index, snap_name in enumerate(snap_names):
        if verbosity:
            print('Now parsing file <{}>, {} of {}, {:.2%}'.format(
                snap_name, snap_index, snap_num, snap_index/snap_num))
        snap = KappaSnapshot(snap_name)
        q = _get_potential_of_snapshot(snap, enzyme, substrate)
        t = snap.get_snapshot_time()
        cat_pot_dist.append([q, t])
    return cat_pot_dist

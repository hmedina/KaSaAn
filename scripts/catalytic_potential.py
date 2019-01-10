#! /usr/local/bin/python3

from KaSaAn import KappaSnapshot, KappaAgent
import warnings
import glob
import argparse
import re
from typing import List


# Helper function to sort file names
def numerical_sort(value):
    parts = re.compile(r'(\d+)').split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts


def get_potential_of_snapshot(file_name: str, enzyme: KappaAgent, substrate: KappaAgent) -> int:
    """"The catalytic potential of a snapshot is a number. Each molecular species will contain a (possibly zero)
    quantity of enzymes, and another of substrates. Their product is the catalytic potential of the species. The sum
    over the species in a snapshot yields the catalytic potential of the snapshot."""
    snap = KappaSnapshot(file_name)
    # Sanity check: both requested agent names are present in the snapshot
    if not enzyme in snap.get_agent_types_present():
        warnings.warn('Agent name <' + enzyme.get_agent_name() + '> + not present in <' + file_name + '>')
    if not substrate in snap.get_agent_types_present():
        warnings.warn('Warning: Agent name <' + substrate.get_agent_name() + '> + not present in <' + file_name + '>')
    # Iterate over each complex and calculate its catalytic potential, q
    cat_pot = 0
    for mol_spec, ab in snap.get_all_complexes_and_abundances():
        e = mol_spec.get_number_of_embeddings_of_agent(enzyme)
        s = mol_spec.get_number_of_embeddings_of_agent(substrate)
        cat_pot += e * s * ab
    return cat_pot


def get_potential_of_folder(base_directory: str, enzyme: KappaAgent, substrate: KappaAgent,
                                      verbosity: bool) -> List[int]:
    # Get the file names of snapshots in specified directory
    snap_names = sorted(glob.glob(base_directory + '*.ka'), key=numerical_sort)
    snap_num = len(snap_names)
    if verbosity:
        print('Found ' + str(snap_num) + ' snapshots in directory ' + base_directory)
    if snap_num < 2:
        warnings.warn('Only one snapshot was found.')
    # Iterate over the files and calculate each's catalytic potential
    cat_pot_dist = []
    snap_num = len(snap_names)
    for snap_index in range(snap_num):
        snap_name = snap_names[snap_index]
        if verbosity:
            print('Now parsing file <{}>, {} of {}, {}%'.format(
                snap_name, snap_index, snap_num, snap_index/snap_num))
        cat_pot_dist.append(get_potential_of_snapshot(snap_name, enzyme, substrate))
    return cat_pot_dist


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-d', '--directory', type=str, default='./',
                        help='The directory containing the snapshots to be analyzed.')
    parser.add_argument('-e', '--enzyme_name', type=str, required=True,
                        help='The name of the agent acting as an enzyme; e.g. <GSK(ARM, FTZ, ser3{ph})> would be simply'
                             ' <GSK>.')
    parser.add_argument('-s', '--substrate_name', type=str, required=True,
                        help='The name of the agent acting as a substrate; e.g. <APC(ARM, OD)> would be simply <APC>.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='If set, print additional information, like number of snapshots found, and current '
                             'snapshot being parsed.')
    parser.add_argument('-o', '--output_file', type=str,
                        help='The name of the file where the list of catalytic potentials should be saved; one value'
                             'per line, in the same order as the snapshots. If not specified, the list will be printed'
                             'to the console.')

    args = parser.parse_args()

    enzyme_agent = KappaAgent(args.enzyme_name)
    substrate_agent = KappaAgent(args.substrate_name)

    q = get_potential_of_folder(args.directory, enzyme_agent, substrate_agent, args.verbose)

    if args.output_file:
        with open(args.output_file, 'w') as out_file:
            for item in q:
                out_file.write('%s\n' % item)
    else:
        print(q)


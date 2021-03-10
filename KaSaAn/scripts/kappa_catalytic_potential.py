#!/usr/bin/env python3

import argparse
import sys

from KaSaAn.functions import get_potential_of_folder


def main(args=None):
    """Out of a series of snapshots from a simulation, obtain the catalytic potential of each snapshot, i.e. each state.
     Each molecular species has a catalytic potential, defined as the product of the number of bound enzyme agents,
     times the number of bound substrate agents, times the abundance of that species. The catalytic potential of a state
     is the sum of the catalytic potentials over all the constituent species."""
    if args is None:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument('-d', '--directory', type=str, default='./',
                        help='The directory containing the snapshots to be analyzed.')
    parser.add_argument('-e', '--enzyme_name', type=str, required=True,
                        help='The name of the agent acting as an enzyme; e.g. <GSK(ARM, FTZ, ser3{ph})> would be simply'
                             ' <GSK>.')
    parser.add_argument('-s', '--substrate_name', type=str, required=True,
                        help='The name of the agent acting as a substrate; e.g. <APC(ARM, OD)> would be simply <APC>.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='If set, print additional information, like number of snapshots found, and current'
                             ' snapshot being parsed.')
    parser.add_argument('-o', '--output_file', type=str,
                        help='The name of the file where the list of catalytic potentials should be saved; one value'
                             ' per line, in the same order as the snapshots. If not specified, the list will be printed'
                             ' to the console.')
    parser.add_argument('-p', '--snapshot_prefix', type=str, required=True,
                        help='The prefix by which the snapshots are named; e.g. <snap_4.ka> would have <snap_>.')

    args = parser.parse_args()

    q = get_potential_of_folder(args.directory, args.enzyme_name, args.substrate_name,
                                args.verbose, args.snapshot_prefix)

    if args.output_file:
        with open(args.output_file, 'w') as out_file:
            for item in q:
                out_file.write('%s\n' % item)
    else:
        print(q)


if __name__ == '__main__':
    main()

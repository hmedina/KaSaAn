#!/usr/bin/env python3

import argparse
import sys

from KaSaAn.functions import prefixed_snapshot_analyzer


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser(
        description='Get cumulative and mean distribution of complex sizes, plus distribution of number of species,'
                    ' based on snapshots sharing a common prefix, like "t_one_snap_7.ka" having the prefix "t_one_".'
                    ' Snapshots must contain the word "snap" and end in ".ka". Files will be produced in the same'
                    ' directory as the snapshots are. They will be prefixed accordingly, e.g.'
                    ' [prefix]distribution_cumulative.csv')
    parser.add_argument('-p', '--prefix', type=str, default='',
                        help='Prefix identifying snapshots to analyze; e.g. "foo_snap_" is the prefix for'
                             ' "foo_snap_76.ka". Files must end with [number].ka')
    parser.add_argument('-d', '--working_directory', type=str, default='./',
                        help='The directory where snapshots are held, and where distribution files will be saved to.')
    parser.add_argument('-v', '--verbosity', action='store_true',
                        help='Print extra information, like number of snapshots found, directory understood, and'
                             ' file names used for output.')
    args = parser.parse_args()
    prefixed_snapshot_analyzer(base_directory=args.working_directory, snap_prefix=args.prefix, verbosity=args.verbosity)


if __name__ == '__main__':
    main()

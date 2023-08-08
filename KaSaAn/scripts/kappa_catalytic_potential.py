#! /usr/bin/env python3
"""
Get the catalytic potential per snapshot for a series.

``` {.text}
usage: kappa_catalytic_potential
[-h]                Show detailed help.
[-d DIRECTORY]      Directory containing the snapshots.
-e ENZYME_NAME      Name of the first agent.
-s SUBSTRATE_NAME   Name of the second agent.
[-v]                If set, print additional information to standard output.
[-o OUTPUT_FILE]    If specified, save to file; else print to standard output.
-p SNAPSHOT_PREFIX  The prefix by which the snapshots are named.
-fs FONT_SIZE       Size of font for all text elements.
```
"""

import argparse
import csv
import matplotlib as mpl
import matplotlib.pyplot as plt
import sys
from pathlib import Path
from KaSaAn.functions import get_potential_of_folder


def main(args=None):
    """Out of a series of snapshots from a simulation, obtain the catalytic potential of each snapshot, i.e. each state.
     Each molecular species has a catalytic potential, defined as the product of the number of bound enzyme agents,
     times the number of bound substrate agents, times the abundance of that species. The catalytic potential of a state
     is the sum of the catalytic potentials over all the constituent species."""
    if args is None:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument('-d', '--directory', type=str, default='.',
                        help='The directory containing the snapshots to be analyzed.')
    parser.add_argument('-e', '--enzyme_name', type=str, required=True,
                        help='The name of the agent acting as an enzyme; e.g. <GSK(ARM, FTZ, ser3{ph})> would be simply'
                             ' <GSK>.')
    parser.add_argument('-s', '--substrate_name', type=str, required=True,
                        help='The name of the agent acting as a substrate; e.g. <APC(ARM, OD)> would be simply <APC>.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='If set, print additional information, like number of snapshots found, and current'
                             ' snapshot being parsed.')
    parser.add_argument('-o', '--output_file', type=Path, default=None,
                        help='The name of the file where the list of catalytic potentials should be saved; one value'
                             ' per line, in the same order as the snapshots. If not specified, the list will be plotted'
                             ' as a function of time.')
    parser.add_argument('-p', '--snapshot_pattern', type=str, default='snap_*.ka',
                        help='Pattern by which the snapshots are named; e.g. <snap_4.ka> would have <snap_*.ka>.')
    parser.add_argument('-ts', '--text_size', type=int,
                        help="If given, set point size for all text elements, overriding MatPlotLib's default.")

    args = parser.parse_args()
    if args.text_size:
        mpl.rcParams['font.size'] = args.text_size

    data = get_potential_of_folder(args.directory, args.enzyme_name, args.substrate_name,
                                   args.verbose, args.snapshot_pattern)

    if args.output_file:
        if not args.output_file.parent.exists():
            args.output_file.parent.mkdir(parents=True)
        with open(args.output_file, 'w') as out_file:
            q_writter = csv.writer(out_file)
            q_writter.writerow(['q', 't'])
            q_writter.writerows(data)
    else:
        _, ax = plt.subplots(layout='constrained')
        q, t = zip(*data)
        ax.plot(t, q)
        ax.set_xlabel('Time')
        ax.set_ylabel('q')
        plt.show()


if __name__ == '__main__':
    main()

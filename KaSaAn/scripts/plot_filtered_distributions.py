#!/usr/bin/env python3

import argparse
import matplotlib.pyplot as plt
import sys

from KaSaAn.functions import plot_filtered_dist


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser(description='View the pseudo-n-mer mass distribution of agents in a snapshot. This'
                                                 ' function filters out all other agents, reporting exclusively the'
                                                 ' abundance of the agent of interest per species. For example, if a'
                                                 ' complex contains 5 agents of type X, 3 of type Y, we will get a'
                                                 ' pentamer if interested in X, a trimer if in Y, which will respectively'
                                                 ' count as 5 Xs or 3 Ys in the mass fraction, per species. The'
                                                 ' collection of all these pseudo-n-mers is reported in histogram format,'
                                                 ' one column per n-mer size.')
    parser.add_argument('-s', type=str, required=True,
                        help='Name of the snapshot file to be viewed.')
    parser.add_argument('-a', type=str, required=True,
                        help='Name of the agent we want to view.')
    parser.add_argument('-p', action='store_true',
                        help='Perfect bins: make one bin per n-mer class. For snapshots with many n-mer classes, this'
                             ' option will yield extremely thin bars, possibly sub-pixel in width (ergo invisible). If'
                             ' unset, the number of bins will be determined by the `doane` estimator (see'
                             ' numpy.histogram for details).')
    parser.add_argument('-c', action='store_true',
                        help='Cumulative plot: make the n-mer abundance cumulative with all smaller n-mers. The height'
                             ' of the last bar will be the total amount of agents of interest in the snapshot.')
    parser.add_argument('-ss', action='store_true',
                        help='Plot species size distribution, rather than agent mass distribution. E.g. in mass, the'
                             ' 3 pentamers count as 15, in size they count as 3.')
    parser.add_argument('-o', type=str,
                        help='Name of output file.')

    args = parser.parse_args()
    my_fig = plot_filtered_dist(snapshot_file_name=args.s, agent_of_interest=args.a, perfect_bins=args.p,
                                cumulative_bins=args.c, plot_raw_counts=args.ss)

    if args.o:
        my_fig.savefig(args.o, bbox_inches='tight')
    else:
        plt.show()


if __name__ == '__main__':
    main()

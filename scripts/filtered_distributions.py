#! /usr/bin/python3

from kappa4_snapshot_analysis import KappaSnapshot
import matplotlib.pyplot as plt
import numpy as np
import argparse


def filtered_dist(snapshot_file_name, agent_of_interest):
    """Given a specific agent of interest, get the filtered size distribution in the snapshot. If the agent appears 5
    times in a complex, interspersed with other agents, it will be reported as a pentamer. The abundance will be that of
    the parent species. This function returns a list of A,B pairs, where A corresponds to the abundance in the species
    (e.g. 5 for pentamer), and B corresponds to the abundance of the parent species."""

    snap = KappaSnapshot(snapshot_file_name)
    assert agent_of_interest in snap.get_agent_types_present(),\
        'Problem: snapshot ' + snapshot_file_name + ' does not contain any agent <<' + agent_of_interest + '>>'
    abundance_in_species = []
    abundance_of_species = []
    for kappa_complex, complex_abundance in snap.get_all_complexes_and_abundances():
        abundance_in_species.append(kappa_complex.get_number_of_embeddings_of_agent(agent_of_interest + '()'))
        abundance_of_species.append(complex_abundance)

    return zip(abundance_in_species, abundance_of_species)


def plot_filtered_dist(snapshot_file_name, agent_of_interest, perfect_bins, cumulative_bins, plot_raw_counts):
    # Unpack data, get maximer value, flatten into a vector
    abundance_in_species, abundance_of_species = zip(*filtered_dist(snapshot_file_name, agent_of_interest))
    if not plot_raw_counts:
        abundance_of_species = [a * b for a,b in zip(abundance_in_species, abundance_of_species)]
    max_mer = max(abundance_in_species)
    flattened_data = np.repeat(abundance_in_species, abundance_of_species)
    # Define figure and plot the data
    fig, ax = plt.subplots()
    plt.hist(x=flattened_data,
             bins=max_mer if perfect_bins else 'doane',
             cumulative=True if cumulative_bins else False,
             range=(1, max_mer + 1),
             align='mid')
    # Annotate axes
    plt.xlabel('Pseudo n-mer size (agents)')
    if plot_raw_counts:
        plt.ylabel('Abundance (molecules)')
    else:
        plt.ylabel('Mass (agents)')

    if cumulative_bins:
        plt.title('Cumulative distribution of pseudo-' + agent_of_interest + '-mers in snapshot')
    else:
        plt.title('Distribution of pseudo-' + agent_of_interest + '-mers in snapshot')

    return fig


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='View the pseudo-n-mer mass distribution of agents in a snapshot. This '
                                                 'function filters out all other agents, reporting exclusively the '
                                                 'abundance of the agent of interest per species. For example, if a '
                                                 'complex contains 5 agents of type X, 3 of type Y, we will get a '
                                                 'pentamer if interested in X, a trimer if in Y, which will respectively'
                                                 'count as 5 Xs or 3 Ys in the mass fraction, per species. The '
                                                 'collection of all these pseudo-n-mers is reported in histogram format,'
                                                 'one column per n-mer size.')
    parser.add_argument('-s', type=str, required=True,
                        help='Name of the snapshot file to be viewed.')
    parser.add_argument('-a', type=str, required=True,
                        help='Name of the agent we want to view.')
    parser.add_argument('-p', action='store_true',
                        help='Perfect bins: make one bin per n-mer class. For snapshots with many n-mer classes, this '
                             'option will yield extremely thin bars, possibly sub-pixel in width (ergo invisible). If '
                             'unset, the number of bins will be determined by the `doane` estimator (see '
                             'numpy.histogram for details).')
    parser.add_argument('-c', action='store_true',
                        help='Cumulative plot: make the n-mer abundance cumulative with all smaller n-mers. The height '
                             'of the last bar will be the total amount of agents of interest in the snapshot.')
    parser.add_argument('-ss', action='store_true',
                        help='Plot species size distribution, rather than agent mass distribution. E.g. in mass, the '
                             '3 pentamers count as 15, in size they count as 3.')
    parser.add_argument('-o', type=str,
                        help='Name of output file.')

    args = parser.parse_args()
    my_fig = plot_filtered_dist(snapshot_file_name=args.s, agent_of_interest=args.a, perfect_bins=args.p,
                                cumulative_bins=args.c, plot_raw_counts=args.ss)

    if args.o:
        plt.savefig(args.o, bbox_inches='tight')
    else:
        plt.show()


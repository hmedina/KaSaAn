#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
from typing import Iterator, Tuple

from ..core import KappaSnapshot, KappaAgent


def filtered_dist(snapshot_file_name: str, agent_of_interest: str) -> Iterator[Tuple[int, int]]:
    """Given a specific agent of interest, get the filtered size distribution in the snapshot. If the agent appears 5
    times in a complex, interspersed with other agents, it will be reported as a pentamer. The abundance will be that of
    the parent species. This function returns a list of A,B pairs, where A corresponds to the abundance in the species
    (e.g. 5 for pentamer), and B corresponds to the abundance of the parent species."""

    snap = KappaSnapshot(snapshot_file_name)
    agent_of_interest = KappaAgent(agent_of_interest)
    if agent_of_interest not in snap.get_agent_types_present():
        raise ValueError('Agent <' + str(agent_of_interest) + '> not in snapshot <' + snapshot_file_name + '>')
    abundance_in_species = []
    abundance_of_species = []
    for kappa_complex, complex_abundance in snap.get_all_complexes_and_abundances():
        abundance_in_species.append(kappa_complex.get_number_of_embeddings_of_agent(agent_of_interest))
        abundance_of_species.append(complex_abundance)

    return zip(abundance_in_species, abundance_of_species)


def plot_filtered_dist(snapshot_file_name: str, agent_of_interest: str, perfect_bins: bool, cumulative_bins: bool,
                       plot_raw_counts: bool):
    # Unpack data, get maximer value, flatten into a vector
    abundance_in_species, abundance_of_species = zip(*filtered_dist(snapshot_file_name, agent_of_interest))
    if not plot_raw_counts:
        abundance_of_species = [a * b for a, b in zip(abundance_in_species, abundance_of_species)]
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

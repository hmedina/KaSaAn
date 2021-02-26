#! /usr/bin/env python3

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy
import warnings
from typing import List, Tuple

from ..core import KappaAgent, KappaSnapshot


def _make_figure(s_times, p_matrix, agent_list, fig_size=mpl.rcParams['figure.figsize'],
                 x_scale='linear', y_scale='linear') -> plt.figure:
    fig, ax = plt.subplots(figsize=fig_size)
    ax.stackplot(s_times, p_matrix, baseline='zero', labels=agent_list)
    ax.set_xlabel('Snapshot time')
    ax.set_ylabel('Abundance of pattern in largest complex')
    fig.legend()
    ax.set_xscale(x_scale)
    ax.set_yscale(y_scale)
    plt.tight_layout()
    return fig


def snapshot_list_to_plot_matrix(snapshot_names, agent_names_requested=None) -> \
        Tuple[List[float], numpy.ndarray, List[KappaAgent]]:
    """See file under `KaSaAn.scripts` for usage."""
    # obtain the composition of the largest complex per snapshot, skipping those
    # snapshots where there is ambiguity
    lc_compositions = []
    snap_times = []
    # type the list of agents, or set as a None to boolean-check later
    if agent_names_requested:
        agents_requested = [KappaAgent(agent_string) for agent_string in agent_names_requested]
    else:
        agents_requested = None
    # iterate over the snapshots
    for snap_name in snapshot_names:
        print('Processing {}, {} of {}'.format(snap_name, snapshot_names.index(snap_name) + 1, len(snapshot_names)))
        snap = KappaSnapshot(snap_name)
        big_o_mers = snap.get_largest_complexes()
        if len(big_o_mers) > 1:
            warnings.warn('Snapshot {} had more than one class of largest complex; omitting it.'.format(
                snap.get_snapshot_file_name()))
            pass
        lc_complex, lc_abundance = big_o_mers[0]
        # filter out agents if requested
        if agents_requested:
            filtered_composition = {}
            for agent in agents_requested:
                filtered_composition[agent] = lc_complex.get_number_of_embeddings_of_agent(agent)
            lc_compositions.append(filtered_composition)
        else:
            lc_compositions.append(lc_complex.get_complex_composition())
        snap_times.append(snap.get_snapshot_time())

    # obtain the superset of agents; used for defining the number of lines to plot
    all_agents = set()
    for compo in lc_compositions:
        all_agents.update(set(compo.keys()))
    all_agents = sorted(all_agents)

    # create matrix for plotting, with alphabetical agent sorting
    plot_matrix = numpy.full([len(all_agents), len(lc_compositions)], numpy.nan, dtype=int)
    for i_compo, compo in enumerate(lc_compositions):
        for i_agent, vi_agent in enumerate(all_agents):
            abundance = compo[vi_agent] if vi_agent in compo else 0
            plot_matrix[i_agent, i_compo] = abundance

    return snap_times, plot_matrix, all_agents

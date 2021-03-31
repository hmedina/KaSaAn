#! /usr/bin/env python3

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy
import warnings
from typing import List, Tuple, Union

from ..core import KappaAgent, KappaComplex, KappaSnapshot


def _make_figure(s_times, p_matrix, agent_list, fig_size=mpl.rcParams['figure.figsize'],
                 x_scale='linear', y_scale='linear', un_stacked: bool = False) -> plt.figure:
    fig, ax = plt.subplots(figsize=fig_size)
    if un_stacked:
        for x, y, n in zip((s_times for item in agent_list), p_matrix, agent_list):
            ax.plot(x, y, label=n)
    else:
        ax.stackplot(s_times, p_matrix, baseline='zero', labels=agent_list)
    ax.set_xlabel('Snapshot time')
    ax.set_ylabel('Abundance of pattern in largest complex')
    fig.legend()
    ax.set_xscale(x_scale)
    ax.set_yscale(y_scale)
    plt.tight_layout()
    return fig


def snapshot_list_to_plot_matrix(snapshot_names, agent_patterns_requested=None, multi_thread: bool = False) -> \
        Tuple[List[float], numpy.ndarray, List[Union[KappaAgent, KappaComplex]]]:
    """See file under `KaSaAn.scripts` for usage."""
    # obtain the composition of the largest complex per snapshot, skipping those
    # snapshots where there is ambiguity
    lc_compositions = []
    snap_times = []
    # iterate over the snapshots
    for snap_name in snapshot_names:
        print('Processing {}, {} of {}'.format(snap_name, snapshot_names.index(snap_name) + 1, len(snapshot_names)))
        snap = KappaSnapshot(snap_name)
        big_o_mers = snap.get_largest_complexes()
        if len(big_o_mers) > 1:
            warnings.warn('Snapshot {} had more than one class of largest complex; omitting it.'.format(
                snap.get_snapshot_file_name()))
            pass
        lc_complex, _ = big_o_mers[0]
        # filter out agents if requested
        if agent_patterns_requested:
            filtered_composition = {}
            for ka_pattern in agent_patterns_requested:
                filtered_composition[ka_pattern] = lc_complex.get_number_of_embeddings(ka_pattern)
            lc_compositions.append(filtered_composition)
        else:
            lc_compositions.append(lc_complex.get_complex_composition())
        snap_times.append(snap.get_snapshot_time())

    # obtain and sort the superset of patterns; used for defining the number of lines to plot
    # a pattern may not have been present in a snapshot, so we need to fill in a zero at some
    # point for that specific snapshot time
    all_patterns = set()
    for compo in lc_compositions:
        all_patterns.update(set(compo.keys()))
    all_patterns = sorted(all_patterns)

    # create matrix for plotting, with alphabetical agent sorting
    plot_matrix = numpy.full([len(all_patterns), len(lc_compositions)], numpy.nan, dtype=int)
    for i_compo, compo in enumerate(lc_compositions):
        for i_pattern, v_pattern in enumerate(all_patterns):
            abundance = compo[v_pattern] if v_pattern in compo else 0
            plot_matrix[i_pattern, i_compo] = abundance

    return snap_times, plot_matrix, all_patterns

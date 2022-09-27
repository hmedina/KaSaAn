#! /usr/bin/env python3

import concurrent.futures as cofu
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy
import warnings
from operator import itemgetter
from typing import Dict, List, Tuple, Set

from ..functions.agent_color_assignment import colorize_observables
from ..core import KappaComplex, KappaSnapshot


def _make_figure(s_times, p_matrix, observable_set: Set[KappaComplex],
                 fig_size=mpl.rcParams['figure.figsize'],
                 x_scale='linear', y_scale='linear',
                 un_stacked: bool = False,
                 supplied_scheme: Dict = None) -> plt.figure:
    fig, ax = plt.subplots(figsize=fig_size)
    # colors for the labels
    color_list = []
    if not supplied_scheme:
        color_scheme = colorize_observables(observable_set)
    else:
        color_scheme = supplied_scheme
    color_list = [color_scheme[obs] for obs in observable_set]
    if un_stacked:
        for x, y, n in zip((s_times for item in observable_set), p_matrix, observable_set):
            ax.plot(x, y, label=n)
    else:
        ax.stackplot(s_times, p_matrix, baseline='zero', labels=observable_set, colors=color_list)
    ax.set_xlabel('Snapshot time')
    ax.set_ylabel('Abundance of pattern in largest complex')
    if not supplied_scheme:
        fig.legend(title='Agents')
    else:
        fig.legend(title='Patterns')
    ax.set_xscale(x_scale)
    ax.set_yscale(y_scale)
    plt.tight_layout()
    return fig


def process_snapshot_helper(snapshot_name: str, patterns_requested: Set[KappaComplex] = None) -> Tuple[float, dict]:
    """Helper function to process snapshots and extract an arbitrary compositon."""
    snap = KappaSnapshot(snapshot_name)
    big_o_mers = snap.get_largest_complexes()
    # obtain the composition of the largest complex per snapshot, skipping those
    # snapshots where there is ambiguity
    if len(big_o_mers) > 1:
        warnings.warn('Snapshot {} had more than one class of largest complex; omitting it.'.format(
            snap.get_snapshot_file_name()))
        return None
    lc_complex, _ = big_o_mers[0]
    # filter out agents if requested
    if patterns_requested:
        filtered_composition = {}
        for ka_pattern in patterns_requested:
            filtered_composition[ka_pattern] = lc_complex.get_number_of_embeddings(ka_pattern)
        lc_composition = filtered_composition
    else:
        lc_composition = lc_complex.get_complex_composition()
    return snap.get_snapshot_time(), lc_composition


def snapshot_list_to_plot_matrix(snapshot_names, patterns_requested: Dict = None, thread_number: int = 1) -> \
        Tuple[List[float], numpy.ndarray, List[KappaComplex]]:
    """See file under `KaSaAn.scripts` for usage."""
    lc_compositions = []
    snap_times = []
    holding_struct = {}
    if patterns_requested:
        pattern_keys: Set[KappaComplex] = patterns_requested.keys()
    else:
        pattern_keys = None
    # iterate over the snapshots
    if thread_number > 1:
        with cofu.ThreadPoolExecutor(max_workers=thread_number) as executor:
            inputs_jobs = ((snap_name, pattern_keys) for snap_name in snapshot_names)
            jobs_submitted = {executor.submit(process_snapshot_helper, *inputs_job): inputs_job
                              for inputs_job in inputs_jobs}
            for job in cofu.as_completed(jobs_submitted):
                input_used = jobs_submitted[job]
                try:
                    job_results = job.result()
                except Exception as exc:
                    print('{} generated an exception: {}'.format(input_used, exc))
                else:
                    if job_results is not None:
                        holding_struct[job_results[0]] = job_results[1]
    else:
        for snap_name in snapshot_names:
            print('Processing {}, {} of {}'.format(snap_name, snapshot_names.index(snap_name) + 1, len(snapshot_names)))
            job_results = process_snapshot_helper(snap_name, pattern_keys)
            if job_results is not None:
                holding_struct[job_results[0]] = job_results[1]
    # sort by snapshot time, split dictionary into two iterables
    snap_times, lc_compositions = zip(*sorted(holding_struct.items(), key=itemgetter(0)))

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

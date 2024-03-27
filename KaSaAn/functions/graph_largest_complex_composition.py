#! /usr/bin/env python3

import concurrent.futures as cofu
import matplotlib as mpl
import matplotlib.figure as mpf
import matplotlib.patches as mppa
import matplotlib.pyplot as plt
import numpy
import warnings
from operator import itemgetter
from typing import Dict, List, Tuple, Set, Union

from KaSaAn.core import KappaAgent

from ..functions.agent_color_assignment import colorize_observables
from ..core import KappaComplex, KappaSnapshot


_stacked_plot_methods = dict(
    first_in_first_out='Patterns are plotted in the order in which they are encountered while reading snapshots.',
    interleaved_initial='Patterns are plotted alternating large and small abundances, as measured in the first snapshot.',
    interleaved_final='Patterns are plotted alternating large and small abundances, as measured in the final snapshot.',
    ascending_initial='Patterns are plotted in ascending abundances, as measured in the first snapshot.',
    ascending_final='Patterns are plotted in ascending abundances, as measured in the final snapshot.',
    descending_initial='Patterns are plotted in descending abundances, as measured in the first snapshot.',
    descending_final='Patterns are plotted in descending abundances, as measured in the final snapshot.'
)


def _make_figure(s_times, p_matrix, observable_set: Set[KappaComplex],
                 fig_size=mpl.rcParams['figure.figsize'],
                 x_scale='linear', y_scale='linear',
                 un_stacked: bool = False,
                 supplied_scheme: Dict = None) -> mpf.Figure:
    fig, ax = plt.subplots(figsize=fig_size, layout='constrained')
    # colors for the labels
    color_list = []
    if not supplied_scheme:
        color_scheme = colorize_observables(observable_set)
    else:
        color_scheme = supplied_scheme
    color_list = [color_scheme[obs] for obs in observable_set]
    if un_stacked:
        for x, y, n in zip((s_times for _ in observable_set), p_matrix, observable_set):
            ax.plot(x, y, label=n)
    else:
        ax.stackplot(s_times, p_matrix, baseline='zero', labels=observable_set, colors=color_list)
    ax.set_xlabel('Snapshot time')
    ax.set_ylabel('Largest complex size')
    # adjust legend's title and content, and order
    if not supplied_scheme:
        leg_h = [mppa.Patch(color=pair[1], label=pair[0].get_agent_name()) for pair in zip(
            observable_set, color_list, strict=True)]
        leg_h.reverse()
        fig.legend(title='Agents', handles=leg_h)
    else:
        leg_h = [mppa.Patch(color=pair[1], label=pair[0]) for pair in zip(
            observable_set, color_list, strict=True)]
        leg_h.reverse()
        fig.legend(title='Patterns', handles=leg_h)
    ax.set_xscale(x_scale)
    ax.set_yscale(y_scale)
    return fig


def process_snapshot_helper(snapshot_name: str, patterns_requested: Set[Union[KappaAgent, KappaComplex]] = None) -> Tuple[float, Dict[Union[KappaAgent, KappaComplex], int]]:
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
        filtered_composition: Dict[Union[KappaAgent, KappaComplex], int] = {}
        for ka_pattern in patterns_requested:
            filtered_composition[ka_pattern] = lc_complex.get_number_of_embeddings(ka_pattern)
        lc_composition = filtered_composition
    else:
        lc_composition = lc_complex.get_complex_composition()
    return snap.get_snapshot_time(), lc_composition


def snapshot_list_to_plot_matrix(
        snapshot_names: List[str],
        patterns_requested: Dict = None,
        thread_number: int = 1,
        stack_order: str = list(_stacked_plot_methods.keys())[0]) -> Tuple[
            List[float],
            numpy.ndarray,
            List[Union[KappaAgent, KappaComplex, Union[KappaAgent, KappaComplex]]]]:
    """See file under `KaSaAn.scripts` for usage."""

    if stack_order not in _stacked_plot_methods.keys():
        UserWarning('Unrecognized order <{}> requested, defaulting to {}.'.format(stack_order, list(_stacked_plot_methods.keys())[0]))

    lc_compositions = []
    snap_times = []
    holding_struct = {}
    if patterns_requested:
        pattern_keys: Set[Union[KappaAgent, KappaComplex]] = patterns_requested.keys()
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
    # in cases where the requested patterns contain KappaAgents and KappaComplexes, the list
    # can't be sorted at once, so they are sorted separately, then concatenated
    all_patterns = set()
    for compo in lc_compositions:
        all_patterns.update(set(compo.keys()))
    if any(isinstance(n, KappaAgent) for n in all_patterns) and any(isinstance(n, KappaComplex) for n in all_patterns):
        agent_patterns = []
        complex_patterns = []
        for some_p in all_patterns:
            if isinstance(some_p, KappaAgent):
                agent_patterns.append(some_p)
            elif isinstance(some_p, KappaComplex):
                complex_patterns.append(some_p)
            else:
                raise ValueError('Unexpected type {} from color scheme! Expected KappaAgent or KappaComplex'.format(type(some_p)))
        all_patterns = sorted(agent_patterns) + sorted(complex_patterns)
    else:
        all_patterns = sorted(all_patterns)

    # create matrix for plotting, with alphabetical agent sorting
    plot_matrix = numpy.full([len(all_patterns), len(lc_compositions)], numpy.nan, dtype=int)
    for i_compo, compo in enumerate(lc_compositions):
        for i_pattern, v_pattern in enumerate(all_patterns):
            abundance = compo[v_pattern] if v_pattern in compo else 0
            plot_matrix[i_pattern, i_compo] = abundance

    # re-order data
    if stack_order == 'first_in_first_out':
        return snap_times, plot_matrix, all_patterns
    else:
        alt_ix_order = []
        sort_strategy, weight_source = stack_order.split('_')
        if sort_strategy == 'interleaved':
            if weight_source == 'initial':
                lower_ix, upper_ix = numpy.array_split(numpy.argsort(plot_matrix[:, 0]), 2)
            else:
                lower_ix, upper_ix = numpy.array_split(numpy.argsort(plot_matrix[:, -1]), 2)
            # the array_split may return arrays of different sizes, so upper_ix may be one element shorter
            #  than lower_ix. If so, the joint-iteration just needs to add the final element from lower_ix
            for ixs in range(len(upper_ix)):
                alt_ix_order.extend([upper_ix[ixs], lower_ix[ixs]])
            if len(lower_ix) != len(upper_ix):
                alt_ix_order.append(lower_ix[-1])
        elif sort_strategy == 'ascending' or sort_strategy == 'descending':
            if weight_source == 'initial':
                alt_ix_order = numpy.argsort(plot_matrix[:, 0])
            else:
                alt_ix_order = numpy.argsort(plot_matrix[:, -1])
            if sort_strategy == 'descending':
                alt_ix_order = numpy.flip(alt_ix_order)
        return snap_times, plot_matrix[alt_ix_order, :], [all_patterns[ix] for ix in alt_ix_order]

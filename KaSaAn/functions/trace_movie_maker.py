#!/usr/bin/env python3

import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from typing import List, Tuple, Set

from .find_snapshot_names import find_snapshot_names
from .snapshot_visualizer_patchwork import process_snapshot, snapshot_composition_simple, colorize_agents, \
    snapshot_legend_simple
from ..core import KappaSnapshot, KappaAgent


def _define_agent_list_and_max_mass(snap_list: List[KappaSnapshot]) -> Tuple[Set[KappaAgent], int]:
    """Define consistent coloring scheme & maximum mass."""
    max_mass = 0
    agent_set = set()
    for snap in snap_list:
        agent_set.update(snap.get_agent_types_present())
        if max_mass < snap.get_total_mass():
            max_mass = snap.get_total_mass()

    return agent_set, max_mass


def movie_from_snapshots(directory: str, vis_mode: str, fig_width: int, xy_ratio: float, dont_scale_mass: bool,
                         legend_cols: int, frame_int: int, verbose: bool):
    """Make a movie out of snapshots. See file under `KaSaAn.scripts` for usage."""
    # Find the snapshots in the directory; determine agent set; colorize it
    snapshots = []
    snapshot_names = find_snapshot_names(target_directory=directory, name_pattern='snapshot.*.ka')
    if verbose:
        print('Found ' + str(len(snapshots)) + ' snapshots in directory ' + directory)
    for snapshot_index, snapshot_name in enumerate(snapshot_names):
        if verbose:
            print('Processing {}, {} of {}'.format(snapshot_name, snapshot_index + 1, len(snapshot_names)))
        snapshots.append(KappaSnapshot(snapshot_name))
    my_agent_list, my_max_mass = _define_agent_list_and_max_mass(snapshots)
    if verbose:
        print('Trace contains ' + str(len(my_agent_list)) + ' agents in total.')
    color_scheme = colorize_agents(my_agent_list)

    # Define figure & sizes
    x_res = 1000
    y_res = x_res * xy_ratio
    fig = plt.figure(figsize=[fig_width, fig_width/2])
    data_ax = fig.add_subplot(121, aspect=1)
    legend_ax = fig.add_subplot(122)
    data_ax.set_xlim(left=0, right=x_res)
    data_ax.set_ylim(bottom=0, top=y_res)
    data_ax.axis('off')

    # Define the animation, i.e. the left axis
    artist_list = []
    final_time = snapshots[-1].get_snapshot_time()
    for snap in snapshots:
        ars = []
        snap_scale = snap.get_total_mass() / my_max_mass if not dont_scale_mass else 1
        if verbose:
            print('Now processing snapshot ' + snap.get_snapshot_file_name())
        data = process_snapshot(snap)
        rectangles, maxi = snapshot_composition_simple(data=data, color_scheme=color_scheme, vis_mode=vis_mode,
                                                       x_res=x_res * snap_scale, y_res=y_res * snap_scale)
        for r in rectangles:
            ar = data_ax.add_patch(r)
            ars.append(ar)
        ars.append(data_ax.text(0, y_res,
                                'Time ' + str(snap.get_snapshot_time()) + ' ; final time ' + str(final_time),
                                horizontalalignment='left', verticalalignment='bottom'))
        ars.append(data_ax.text(x_res, y_res, 'Mass present ' + str(snap.get_total_mass()),
                                horizontalalignment='right', verticalalignment='bottom'))
        artist_list.append(ars)

    # Define the legend, i.e. the right axis
    # This legend will have legend_cols number of columns for writing the agents. This helps with scaling for systems
    # with a large number of agents. The limits of this section are determined based on the number of agents to draw.
    legend_squares, legend_texts = snapshot_legend_simple(color_scheme=color_scheme, col_num=legend_cols)
    legend_ax.add_collection(PatchCollection(legend_squares, match_original=True))
    for text in legend_texts:
        legend_ax.add_artist(text)
    legend_ax.set_xlim(left=0, right=legend_cols)
    legend_ax.set_ylim(top=1, bottom=-divmod(len(color_scheme), legend_cols)[0] - 1)
    legend_ax.axis('off')

    # Make movie out of list
    if verbose:
        print('Now collecting rectangles into an animation.')
    ani = animation.ArtistAnimation(fig=fig, artists=artist_list, interval=frame_int, repeat_delay=2000)

    return ani

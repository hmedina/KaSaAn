#! /usr/local/bin/python3

import glob
import re
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.collections import PatchCollection
from visualization.snapshot_visualizer import process_snapshot, snapshot_composition_simple, colorize_agents, snapshot_legend_simple
from KaSaAn import KappaSnapshot, KappaAgent
import argparse
from typing import List, Tuple, Set


# Helper function to sort file names
def numerical_sort(value):
    parts = re.compile(r'(\d+)').split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts


# Get & sort the file names
def find_snapshot_files(base_dir: str = './') -> List[KappaSnapshot]:
    # In case we're fed a directory name, without the trailing slash, append it
    if base_dir[-1] != '/':
        base_dir += '/'
    snap_names = sorted(glob.glob(base_dir + 'snapshot.*.ka'), key=numerical_sort)
    snapshot_list = []
    for file_name in snap_names:
        snapshot_list.append(KappaSnapshot(file_name))

    return snapshot_list


# Define consistent coloring scheme & maximum mass
def define_agent_list_and_max_mass(snap_list: List[KappaSnapshot]) -> Tuple[Set[KappaAgent], int]:
    max_mass = 0
    agent_set = set()
    for snap in snap_list:
        agent_set.update(snap.get_agent_types_present())
        if max_mass < snap.get_total_mass():
            max_mass = snap.get_total_mass()

    return agent_set, max_mass


# Master function
def movie_from_snapshots(directory: str, vis_mode: str, fig_width: int, xy_ratio: float, dont_scale_mass: bool,
                         legend_cols: int, frame_int: int, verbose: bool):
    # Find the snapshots in the directory; determine agent set; colorize it
    snapshots = find_snapshot_files(directory)
    if verbose:
        print('Found ' + str(len(snapshots)) + ' snapshots in directory ' + directory)
    my_agent_list, my_max_mass = define_agent_list_and_max_mass(snapshots)
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
                                'Time ' + str(snap.get_snapshot_time()) + ' ; final time ' + str(snapshots[-1].get_snapshot_time()),
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Make a movie out of a set of snapshot files, and save it to disk.')
    parser.add_argument('-d', '--directory', type=str, default='./',
                        help='Directory where the snapshots are located. These should be named "snapshot.#.ka", i.e.'
                             'the default naming scheme used by the Kappa Trace Query Language Engine. Default uses '
                             'current directory.')
    parser.add_argument('-m', '--vis_mode', type=str, default='mass', choices=['mass', 'count', 'size'],
                        help='Specify the type of visualization to render. Default uses mass.')
    parser.add_argument('-o', '--output_file', type=str, default='',
                        help='Optional name of file for saving the movie. If unset, the movie will be shown instead,'
                             'using a TK window.')
    parser.add_argument('-w', '--fig_width', type=int, default=16,
                        help='Number of inches for the width of the plot. Figure will be 2 times this value wide, with'
                             'the plot being this value wide and the legend being this value wide. Default value is 16.')
    parser.add_argument('-r', '--XY_ratio', type=float, default=1.0,
                        help='X to Y ratio of the plot. Default value is 1: isometric view.')
    parser.add_argument('-s', '--do_not_scale_mass', action='store_true',
                        help='Rescale each snapshot to use the total plot area? If specified, each snapshot will be'
                             'viewed using the entire plot area: the amount of mass a pixel will represent will not be '
                             'consistent across snapshots (unless there is neither creation nor deletion of agents in'
                             'the model).')
    parser.add_argument('-l', '--legend_columns', type=int, default=2,
                        help='Number of columns in the legend. Increase this number to have more entries per row.'
                             'Default value is 2.')
    parser.add_argument('-f', '--frame_interval', type=int, default=500,
                        help='Number of mili-seconds between frames in the animation.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Display information about number of snapshots found.')
    args = parser.parse_args()


    my_animation = movie_from_snapshots(directory=args.directory,
                                        vis_mode=args.vis_mode,
                                        fig_width=args.fig_width,
                                        xy_ratio=args.XY_ratio,
                                        dont_scale_mass=args.do_not_scale_mass,
                                        legend_cols=args.legend_columns,
                                        frame_int=args.frame_interval,
                                        verbose=args.verbose)

    # Save to file, or show the figure
    if args.output_file:
        if args.verbose:
            print('Now saving animation to file.')
        my_animation.save(args.output_file)
    else:
        plt.show()


#! /usr/bin/env python3

import argparse
import matplotlib as mpl
import matplotlib.pyplot as plt
from pathlib import Path

from KaSaAn.functions import find_snapshot_names
from KaSaAn.functions.graph_largest_complex_composition import snapshot_list_to_plot_matrix, make_figure


def main():
    parser = argparse.ArgumentParser(
        description='Plot the evolution of the giant component in time from a set of snapshots located in a directory,'
                    ' showing only the subset of agents specified.')
    parser.add_argument('-d', '--directory', type=str, default='.',
                        help='Name of the directory where snapshots are stored.')
    parser.add_argument('-p', '--pattern', type=str, default='snap*.ka',
                        help='Pattern that should be used to get the snapshot names; default is as produced by KaSim.')
    parser.add_argument('-a', '--agents', type=str, default=None, nargs='*',
                        help='Name of the agents that should be plotted; leave blank or omit to plot all. Supports site'
                             ' specification; does not follow bonds.')
    parser.add_argument('-o', '--output_name', type=str,
                        help='If specified, the name of the file where the figure should be saved. If not given,'
                             ' figure will be shown instead. If alternate scale options are given, a "_log_lin" or similar'
                             ' will be inserted between the file-name and the extension requested to distinguish the'
                             ' additional requested files.')
    parser.add_argument('-fs', '--figure_size', type=float, default=mpl.rcParams['figure.figsize'], nargs=2,
                        help='Size of the resulting figure, in inches, specified as two elements, width and height'
                             ' (text size is specified in points, so this affects the size of text relative to other'
                             ' graph elements).')
    parser.add_argument('--lin_log', action='store_true',
                        help='If specified, produce an additional plot with linear X-axis and logarithmic Y-axis.')
    parser.add_argument('--log_lin', action='store_true',
                        help='If specified, produce an additional plot with logarithmic X-axis and linear Y-axis.')
    parser.add_argument('--log_log', action='store_true',
                        help='If specified, produce an additional plot with logarithmic X-axis and logarithmic Y-axis.')

    args = parser.parse_args()

    snap_name_list = find_snapshot_names(target_directory=args.directory, name_pattern=args.pattern)
    s_times, p_matrix, agent_list = snapshot_list_to_plot_matrix(snapshot_names=snap_name_list,
                                                                 agent_names_requested=args.agents)
    # scale plot
    fig_lin_lin = make_figure(s_times, p_matrix, agent_list, args.figure_size, 'linear', 'linear')
    if args.lin_log:
        fig_lin_log = make_figure(s_times, p_matrix, agent_list, args.figure_size, 'linear', 'log')
    if args.log_lin:
        fig_log_lin = make_figure(s_times, p_matrix, agent_list, args.figure_size, 'log', 'linear')
    if args.log_log:
        fig_log_log = make_figure(s_times, p_matrix, agent_list, args.figure_size, 'log', 'log')
    # save or display?
    if args.output_name:
        save_path = Path(args.output_name)
        fig_lin_lin.savefig(save_path)
        if args.lin_log:
            fig_lin_log.savefig(save_path.parents[0] / Path(save_path.name + '_lin_log' + save_path.suffix))
        if args.log_lin:
            fig_log_lin.savefig(save_path.parents[0] / Path(save_path.name + '_log_lin' + save_path.suffix))
        if args.log_log:
            fig_log_log.savefig(save_path.parents[0] / Path(save_path.name + '_log_log' + save_path.suffix))
    else:
        plt.show()


if __name__ == '__main__':
    main()

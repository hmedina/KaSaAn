#! /usr/bin/env python3
"""
Plot the compostion of the giant component in time from a set of snapshots located in a directory.

``` {.text}
usage: kappa_snapshot_largest_complex_time
[-h]                    Show detailed help.
[-d DIRECTORY]          Directory where snapshots are stored, default is <.>
[-p PATTERN]            Pattern that groups desired snapshots names; default 'snap*.ka'.
[-a [...]]              Patterns that should be plotted; omiting plots sum formula.
[-o OUTPUT_NAME]        The common file name for saving figures; shown if not given.
[-fs WIDTH HEIGHT]      Size of the resulting figure, in inches.
[--lin_log]             If specified, produce an additional plot with linear X-axis and logarithmic Y-axis.
[--log_lin]             If specified, produce an additional plot with logarithmic X-axis and linear Y-axis.
[--log_log]             If specified, produce an additional plot with logarithmic X-axis and logarithmic Y-axis.
[--un_stacked]          If given, produce regular non-stacked plot.
[--mt THREADS]          Launch multiple threads for reading snapshots. Safe, but always less performant: WIP.
```
"""

import argparse
import matplotlib as mpl
import matplotlib.pyplot as plt
from pathlib import Path

from KaSaAn.functions import find_snapshot_names
from KaSaAn.functions.graph_largest_complex_composition import snapshot_list_to_plot_matrix, _make_figure


def main():
    """Plot the evolution of the giant component in time from a set of snapshots located in a directory, showing only
    the subset of patterns specified."""
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument('-d', '--directory', type=str, default='.',
                        help='Name of the directory where snapshots are stored; default is current directory.')
    parser.add_argument('-p', '--pattern', type=str, default='snap*.ka',
                        help='Pattern that should be used to get the snapshot names; default is as produced by KaSim,'
                        ' `snap*.ka`')
    parser.add_argument('-a', '--agent-patterns', type=str, default=None, nargs='*',
                        help='Patterns whose number of symmetry-adjusted embeddings into the giant component'
                             ' should be plotted; leave blank or omit to plot all agent types (i.e. sum formula)'
                             ' instead.')
    parser.add_argument('-o', '--output_name', type=str,
                        help='If specified, the name of the file where the figure should be saved. If not given,'
                             ' figure will be shown instead. If alternate scale options are given, a "_log_lin" or'
                             ' similar will be inserted between the file-name and the extension requested to'
                             ' distinguish the additional requested files.')
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
    parser.add_argument('--un_stacked', action='store_true',
                        help='If given, produce a conventional plot rather than a filled stacked plot (meant for sum'
                        ' formulae). Useful when plotting patterns that may overlap, ergo whose stacking would not be'
                        ' as intuitive.')
    parser.add_argument('-mt', '--multi_thread', type=int, default=1,
                        help='Number of threads for the concurrent pool of workers to read-in snapshots. Default uses'
                        ' 1, so a single-threaded for-loop.')

    args = parser.parse_args()

    snap_name_list = find_snapshot_names(target_directory=args.directory, name_pattern=args.pattern)
    s_times, p_matrix, pattern_list = snapshot_list_to_plot_matrix(snapshot_names=snap_name_list,
                                                                   agent_patterns_requested=args.agent_patterns,
                                                                   thread_number=args.multi_thread)
    # scale plot
    fig_lin_lin = _make_figure(s_times, p_matrix, pattern_list, args.figure_size, 'linear', 'linear', args.un_stacked)
    if args.lin_log:
        fig_lin_log = _make_figure(s_times, p_matrix, pattern_list, args.figure_size, 'linear', 'log', args.un_stacked)
    if args.log_lin:
        fig_log_lin = _make_figure(s_times, p_matrix, pattern_list, args.figure_size, 'log', 'linear', args.un_stacked)
    if args.log_log:
        fig_log_log = _make_figure(s_times, p_matrix, pattern_list, args.figure_size, 'log', 'log', args.un_stacked)
    # save or display?
    if args.output_name:
        save_path = Path(args.output_name)
        fig_lin_lin.savefig(save_path)
        if args.lin_log:
            fig_lin_log.savefig(save_path.parents[0] / Path(save_path.stem + '_lin_log' + save_path.suffix))
        if args.log_lin:
            fig_log_lin.savefig(save_path.parents[0] / Path(save_path.stem + '_log_lin' + save_path.suffix))
        if args.log_log:
            fig_log_log.savefig(save_path.parents[0] / Path(save_path.stem + '_log_log' + save_path.suffix))
    else:
        plt.show()


if __name__ == '__main__':
    main()

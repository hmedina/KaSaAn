#! /usr/bin/env python3
"""
Plot the compostion of the giant component in time from a set of snapshots located in a directory.

``` {.text}
usage: kappa_snapshot_largest_complex_time [-h] [-d DIRECTORY] [-p PATTERN] [-cs COLORING_SCHEME] [-o OUTPUT_NAME] [-fs WIDTH HEIGHT] [--lin_log] [--log_lin] [--log_log] [--un_stacked] [-mt MULTI_THREAD] [-ts TEXT_SIZE]
[-h]                    Show detailed help.
[-d DIRECTORY]          Directory where snapshots are stored, default is <.>
[-p PATTERN]            Pattern that groups desired snapshots names; default 'snap*.ka'.
[-cs FILE]              Optional file containing a dictionary with color scheme to use for species composition. E.g.
                        <{"Bob": #fff, "Mary": #999, "Sue": #222}>, where the color can be anything converable to a
                        color by MatPlotLib (e.g. RGB[A] tuples, hex-strings, XKCD colors...). Supports KappaAgents,
                        with or without agent signature, as well as KappaComplexes. If not provided, the sum formula
                        will be displayed (arbitrary colors per agent, discarding agent signature).
[-o OUTPUT_NAME]        The common file name for saving figures; shown if not given.
[-fs WIDTH HEIGHT]      Size of the resulting figure, in inches.
[--lin_log]             If specified, produce an additional plot with linear X-axis and logarithmic Y-axis.
[--log_lin]             If specified, produce an additional plot with logarithmic X-axis and linear Y-axis.
[--log_log]             If specified, produce an additional plot with logarithmic X-axis and logarithmic Y-axis.
[--un_stacked]          If given, produce regular non-stacked plot.
[--mt THREADS]          Launch multiple threads for reading snapshots. Safe, but always less performant: WIP.
[-ts TEXT_SIZE]         Override default size for text, in points.
```
"""

import argparse
import ast
import matplotlib as mpl
import matplotlib.pyplot as plt
from pathlib import Path
from KaSaAn.core.KappaError import ComplexParseError, AgentParseError
from KaSaAn.core.KappaAgent import KappaAgent
from KaSaAn.core.KappaComplex import KappaComplex
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
    parser.add_argument('-cs', '--coloring_scheme', type=str,
                        help='Optional file containing a dictionary with color scheme to use for species composition.'
                             ' E.g. <{"Bob": #fff, "Mary": #999, "Sue": #222}>, where the color can be anything'
                             ' converable to a color by MatPlotLib (e.g. RGB[A] tuples, hex-strings, XKCD colors...).'
                             ' Supports KappaAgents, with or without agent signature, as well as KappaComplexes.'
                             ' If not provided, the sum formula will be displayed (arbitrary colors per agent,'
                             ' discarding agent signature).')
    parser.add_argument('-o', '--output_name', type=Path, default=None,
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
    parser.add_argument('-ts', '--text_size', type=int,
                        help="If given, set point size for all text elements, overriding MatPlotLib's default.")

    args = parser.parse_args()

    if args.text_size:
        mpl.rcParams['font.size'] = args.text_size

    # for user-defined coloring schemes, read the dictionary from a file, convert keys
    # Since single-agents can be interpreted as KappaComplexes, and that preserves sorting & comparisons, we cast
    # as KappaComplexes all keys, even if KappaAgent could be a smaller representation.
    if args.coloring_scheme:
        coloring_scheme = {}
        with open(args.coloring_scheme, 'r') as cs_file:
            coloring_scheme_raw = ast.literal_eval(cs_file.read())
            for key, value in coloring_scheme_raw.items():
                try:
                    coloring_scheme[KappaAgent(key)] = value
                except AgentParseError:
                    try:
                        coloring_scheme[KappaComplex(key)] = value
                    except ComplexParseError:
                        raise ValueError('Could not parse {} as a KappaComplex nor a KappaAgent'.format(key))
    else:
        coloring_scheme = None

    snap_name_list = find_snapshot_names(target_directory=args.directory, name_pattern=args.pattern)
    s_times, p_matrix, pattern_list = snapshot_list_to_plot_matrix(snapshot_names=snap_name_list,
                                                                   patterns_requested=coloring_scheme,
                                                                   thread_number=args.multi_thread)
    # scale plot
    fig_lin_lin = _make_figure(s_times, p_matrix, pattern_list, args.figure_size,
                               'linear', 'linear', args.un_stacked, coloring_scheme)
    if args.lin_log:
        fig_lin_log = _make_figure(s_times, p_matrix, pattern_list, args.figure_size,
                                   'linear', 'log', args.un_stacked, coloring_scheme)
    if args.log_lin:
        fig_log_lin = _make_figure(s_times, p_matrix, pattern_list, args.figure_size,
                                   'log', 'linear', args.un_stacked, coloring_scheme)
    if args.log_log:
        fig_log_log = _make_figure(s_times, p_matrix, pattern_list, args.figure_size,
                                   'log', 'log', args.un_stacked, coloring_scheme)
    # save or display?
    if args.output_name:
        save_path: Path = args.output_name.parent
        if not save_path.exists():
            save_path.mkdir(parents=True)
        fig_lin_lin.savefig(args.output_name)
        if args.lin_log:
            fig_lin_log.savefig(
                save_path / Path(args.output_name.stem + '_lin_log' + args.output_name.suffix))
        if args.log_lin:
            fig_log_lin.savefig(
                save_path / Path(args.output_name.stem + '_log_lin' + args.output_name.suffix))
        if args.log_log:
            fig_log_log.savefig(
                save_path / Path(args.output_name.stem + '_log_log' + args.output_name.suffix))
    else:
        plt.show()


if __name__ == '__main__':
    main()

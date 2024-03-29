#!/usr/bin/env python3
"""
Plot a trace file produced by KaSim.

``` {.text}
usage: kappa_observable_plotter [-h] [-i INPUT_FILE_NAME] [-o OUTPUT_FILE_NAME] [-p PRINT_OBSERVABLES_TO_FILE] [-vi [VARIABLE_INDEXES ...]] [-vn [VARIABLE_NAMES ...]] [-ve [VARIABLE_EXPRESSIONS ...]] [-fs WIDTH HEIGHT] [--limit_left LIMIT_LEFT] [--limit_right LIMIT_RIGHT] [--limit_bottom LIMIT_BOTTOM] [--limit_top LIMIT_TOP] [-d] [-lx] [-ly] [-ts TEXT_SIZE] [--legend_loc {upper left,upper center,upper right,center left,center,center right,lower left,lower center,lower right,outside right upper,outside right lower,outside left upper,outside left lower}] [--legend_ncol LEGEND_NCOL]
[-h]                            Show detailed help.
[-i INPUT_FILE_NAME]            File to be plotted, <data.csv> if omitted.
[-o OUTPUT_FILE_NAME]           If given, save plot to file; else show.
[-p FILE_NAME]                  Dump ordered observables to file, one per line, for indexing.
[-vi [...]]                     The list of observable indexes to be plotted; all if omitted.
[-vn [...]]                     The name of observables to be plotted; all if omitted.
[-ve [...]]]                    Algebraic expressions of variable names.
[-fs WIDTH HEIGHT]              Size of the resulting figure, in inches.
[--limit_left X_MIN]            Override left limit of plot.
[--limit_right X_MAX]           Override right limit of plot.
[--limit_bottom Y_MIN]          Override bottom limit of plot.
[--limit_top Y_MAX]             Override top limit of plot.
[-d]                            If passed, plot discrete differential over time.
[-lx]                           Plot the X axis in logarithmic scale.
[-ly]                           Plot the Y axis in logarithmic scale.
[-ts TEXT_SIZE]                 Override default size for text, in points.
[--legend_loc {...} ]           Specify legend location; <outside> options plot outside axes. Options are:
                                    upper left, upper center, upper right,
                                    center left, center, center right,
                                    lower left, lower center, lower right,
                                    outside left upper, outside right upper,
                                    outside left lower, outside right lower
[--legend_ncol LEGEND_NCOL]     Number of columns for the legend.
[--text_instead_of_paths]       Output text elements instead of paths; embeds used glyphs
```
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
from argparse import ArgumentParser
from pathlib import Path
from KaSaAn.functions import observable_file_reader, observable_list_axis_annotator


def main():
    """Plot a trace file produced by KaSim."""
    parser = ArgumentParser(description=main.__doc__)
    parser.add_argument('-i', '--input_file_name', type=str, default='data.csv',
                        help='Name of the file with the time series traces to be plotted. By default it will look for'
                             ' <data.csv>')
    parser.add_argument('-o', '--output_file_name', type=Path, default=None,
                        help='Name of the file to where the figure should be saved; displayed if not specified.')
    parser.add_argument('-p', '--print_observables_to_file', type=str, default='',
                        help="If specified, dump the list of observables to a file, one per line, so that the line"
                             " number corresponds to the observable's index.")
    parser.add_argument('-vi', '--variable_indexes', type=int, default=None, nargs='*',
                        help='The list of variable / observable indexes that should be plotted. Observables are plotted'
                             ' in their declaration order, see option <-p> to print their order. If neither <-vi> nor'
                             ' <-vn> are specified, all variables will be plotted. Options <-vi> and <-vn> can be '
                             'called together, and their set will be plotted. Ignored with <-ve>.')
    parser.add_argument('-vn', '--variable_names', type=str, default='', nargs='*',
                        help='List of variable names that should be plotted. If neither <-vi> nor <-vn> are specified,'
                             ' all variables will be plotted. Options <-vi> and <-vn> can be called together, and their'
                             ' set will be plotted. Ignored with <-ve>.')
    parser.add_argument('-ve', '--variable_expressions', type=str, default='', nargs='*',
                        help='A list of strings, each with one algebraic expression using variable names held in the'
                             ' file (e.g. -ve \'"Axn.Axn" / "Axn"\' \'1 - ( "Axn.Axn" / "Axn")\')')
    parser.add_argument('-fs', '--fig_size', type=float, default=mpl.rcParams['figure.figsize'], nargs=2,
                        help='Size of the resulting figure, in inches, specified as two elements, width and height '
                             '(text size is specified in points, so this affects the size of text relative to other'
                             ' graph elements).')
    parser.add_argument('--limit_left', type=float, default=None,
                        help='Override the left limit of the plot. If the left limit is greater than the right limit,'
                             ' X-axis values will decrease from left to right.')
    parser.add_argument('--limit_right', type=float, default=None,
                        help='Override the right limit of the plot.')
    parser.add_argument('--limit_bottom', type=float, default=None,
                        help='Override the bottom limit of the plot. If the bottom limit is greater than the top'
                        ' limit, Y-axis values will decrease from bottom to top.')
    parser.add_argument('--limit_top', type=float, default=None,
                        help='Override the top limit of the plot.')
    parser.add_argument('-d', '--differential', action='store_true',
                        help="If passed, variables will be derived using numpy's diff method; useful for getting a rate"
                             " out of a counter generated by a rule's firing.")
    parser.add_argument('-lx', '--log_x', action='store_true',
                        help='Plot the X axis in logarithmic scale.')
    parser.add_argument('-ly', '--log_y', action='store_true',
                        help='Plot the Y axis in logarithmic scale.')
    parser.add_argument('-ts', '--text_size', type=int,
                        help="If given, set point size for all text elements, overriding MatPlotLib's default.")
    parser.add_argument('--legend_loc', type=str, choices=[
        'upper left', 'upper center', 'upper right',
        'center left', 'center', 'center right',
        'lower left', 'lower center', 'lower right',
        'outside right upper', 'outside right lower', 'outside left upper', 'outside left lower'],
                        help='Override location of the legend. Options prefixed with <outside> plot outside the axes.')
    parser.add_argument('--legend_ncol', type=int, default=1,
                        help='Number of columns for the legend.')
    parser.add_argument('--text_instead_of_paths', action='store_true',
                        help='If set, figure will embed used glyphs and export text elements, instead of rendering the'
                             ' glyphs into paths. Only supported for PDF export.')
    args = parser.parse_args()

    if args.text_size:
        mpl.rcParams['font.size'] = args.text_size
    if args.text_instead_of_paths:
        plt.rcParams['pdf.fonttype'] = 42

    this_data = observable_file_reader(args.input_file_name)

    fig, ax = plt.subplots(figsize=args.fig_size, layout='constrained')
    observable_list_axis_annotator(obs_axis=ax, data=this_data,
                                   vars_indexes=args.variable_indexes,
                                   vars_names=args.variable_names,
                                   vars_exprs=args.variable_expressions,
                                   axis_x_log=args.log_x, axis_y_log=args.log_y,
                                   diff_toggle=args.differential,
                                   add_legend=False)
    if args.legend_loc is not None:
        fig.legend(loc=args.legend_loc, ncol=args.legend_ncol)
    else:
        ax.legend(loc='best', ncol=args.legend_ncol)
    ax.set_xlim(left=args.limit_left, right=args.limit_right)
    ax.set_ylim(bottom=args.limit_bottom, top=args.limit_top)

    # print out observables
    if args.print_observables_to_file:
        with open(args.print_observables_to_file, 'w') as file:
            for obs in this_data[0]:
                file.write(obs + '\n')

    # save or display the figure
    if args.output_file_name:
        if not args.output_file_name.parent.exists():
            args.output_file_name.parent.mkdir(parents=True)
        fig.savefig(fname=args.output_file_name)
    else:
        plt.show()


if __name__ == '__main__':
    main()

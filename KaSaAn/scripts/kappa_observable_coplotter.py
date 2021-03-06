#! /usr/bin/env python3
"""
Plot a variable from several output files.

``` {.text}
usage: kappa_observable_coplotter
[-h]                        Show detailed help.
-p PATTERN                  (quoted) Pattern matching desired files.
[-vi VARIABLE_BY_INDEX]     Index of the variable to be co-plotted.
[-vn VARIABLE_BY_NAME]      Name of the variable to be co-plotted.
[-o OUT_FILE]               If given, save plot to file; else show.
[-d]                        If passed, plot discrete differential over time.
[-fs WIDTH HEIGHT]          Size of the resulting figure, in inches.
[-lx]                       Plot the X axis in logarithmic scale.
[-ly]                       Plot the Y axis in logarithmic scale.
```
"""

import argparse
import matplotlib as mpl
import matplotlib.pyplot as plt
from KaSaAn.functions import observable_coplot_axis_annotator


def main():
    """Co-plot the same variable from multiple files, save as file or display the figure."""
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument('-p', '--pattern', type=str, required=True,
                        help='Pattern, passed to glob.glob that would match the desired files to co-plot, should'
                             ' probably be quoted.')
    parser.add_argument('-vi', '--variable_by_index', type=int, default=None,
                        help='Index of the variable to be co-plotted. Index is the order of declaration (i.e. var #1'
                             ' plot is observable #1), or column as printed in the out_file.csv from KaSim (i.e. var #1'
                             ' plots column #1).')
    parser.add_argument('-vn', '--variable_by_name', type=str, default='',
                        help='Name of the variable to be co-plotted.')
    parser.add_argument('-o', '--out_file', type=str, default='',
                        help='Name of the file where the figure should be saved. If left blank or omitted, the figure'
                             ' will be shown instead.')
    parser.add_argument('-d', '--differential', action='store_true',
                        help="If passed, variable will be derived using numpy's diff method; useful for getting a rate"
                             " out of a counter generated by a rule's firing.")
    parser.add_argument('-fs', '--figure_size', type=float, default=mpl.rcParams['figure.figsize'], nargs=2,
                        help='Size of the resulting figure, in inches, specified as two elements, width and height'
                             ' (text size is specified in points, so this affects the size of text relative to other'
                             ' graph elements).')
    parser.add_argument('-lx', '--log_x', action='store_true',
                        help='Plot the X axis in logarithmic scale.')
    parser.add_argument('-ly', '--log_y', action='store_true',
                        help='Plot the Y axis in logarithmic scale.')
    args = parser.parse_args()
    fig, ax = plt.subplots(figsize=args.figure_size)
    observable_coplot_axis_annotator(target_axis=ax,
                                     file_pattern=args.pattern,
                                     variable_index=args.variable_by_index,
                                     variable_name=args.variable_by_name,
                                     differential_toggle=args.differential,
                                     log_axis_x=args.log_x,
                                     log_axis_y=args.log_y)
    if args.out_file:
        plt.tight_layout()
        fig.savefig(args.out_file)
    else:
        plt.show()


if __name__ == '__main__':
    main()

#! /usr/bin/env python3
"""
Render a contact map.
"""

import argparse
import matplotlib as mpl
import matplotlib.pyplot as plt
from KaSaAn.core import KappaContactMap
from KaSaAn.core.KappaContactMap import valid_graph_layouts


def main():
    """Plot a contact map taken from a witness file, e.g. `inputs.ka`"""

    w: int = max([len(key) for key in valid_graph_layouts.keys()])    # key width, for prettier printing
    layout_expl: str = '\n'.join(['{:<{width}}\t{}'.format(n, v.__doc__.split('\n')[0], width=w)
                                  for n, v in valid_graph_layouts.items()])

    parser = argparse.ArgumentParser(description=main.__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-i', '--input_file_name', type=str, default='inputs.ka',
                        help='Name of the file containing the contact map, written in kappa by the Kappa Static'
                        ' Analyzer (KaSA). By default, will search for `inputs.ka`, aka the "witness file".')
    # ToDo
    # parser.add_argument('-cs', '--coloring_scheme', type=str, default='',
    #                     help='Name of the file containing a coloring scheme for drawing the faces of the wedges that'
    #                     ' represent the agents.')
    parser.add_argument('-fs', '--fig_size', type=float, default=mpl.rcParams['figure.figsize'], nargs=2,
                        help='Size of the resulting figure, in inches, specified as two elements, width and height'
                        ' (text size is specified in points, so this affects the size of text relative to other'
                        ' graph elements).')
    parser.add_argument('-o', '--output_file_name', type=str, default=None,
                        help='Name of the file to where the figure should be saved; displayed if not specified.')
    parser.add_argument('-m', '--method', type=str, choices=list(valid_graph_layouts.keys()), default='',
                        help='Interpret contact map as a plain graph and layout using one of these:\n' + layout_expl)
    parser.add_argument('--summarize_flagpole', action='store_true',
                        help='If passed, summarizes state-only sites as a numeric annotation on a special wedge'
                        ' (the flagpole). Otherwise, these sites and their states are listed in said flagpole.')
    parser.add_argument('--keep_axes_ticks', action='store_true',
                        help='If given, will keep the X & Y axes ticks; use this to estimate coordinates and offsets'
                        ' for manual agent placement.')
    args = parser.parse_args()

    this_cm = KappaContactMap(args.input_file_name)
    fig, ax = plt.subplots(figsize=args.fig_size)

    if args.method != '':
        this_cm.layout_from_graph(args.method)
    this_cm.draw(ax, draw_state_flagpole=(not args.summarize_flagpole))

    if not args.keep_axes_ticks:
        ax.axis('off')

    plt.tight_layout()

    if args.output_file_name:
        fig.savefig(args.output_file_name)
    else:
        # ToDo add widgets for manual control
        plt.show()


if __name__ == '__main__':
    main()
